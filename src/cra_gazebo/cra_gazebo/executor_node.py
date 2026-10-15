"""Distance-limited drive skill for the CRA Gazebo demonstration."""
import math
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from cra_msgs.msg import Intent, ExecutionState


class GazeboExecutor(Node):
    def __init__(self):
        super().__init__('cra_gazebo_executor')
        self.command = self.create_publisher(Twist, '/cra/base/cmd_vel', 10)
        self.feedback = self.create_publisher(ExecutionState, '/cra/execution_state', 10)
        self.create_subscription(Intent, '/cra/intent', self.on_intent, 10)
        self.create_subscription(Odometry, '/cra/base/odom', self.on_odom, 10)
        self.state = 'IDLE'
        self.intent = Intent()
        self.position = None
        self.last_odom = 0.0
        self.origin = None
        self.target = 0.0
        self.progress = 0.0
        self.detail = 'Waiting for move_forward [distance_metres]'
        self.pending_error = None
        self.started = 0.0
        self.create_timer(0.05, self.tick)

    def on_odom(self, msg):
        self.position = (msg.pose.pose.position.x, msg.pose.pose.position.y)
        self.last_odom = time.monotonic()

    def on_intent(self, msg):
        if self.state == 'EXECUTING':
            self.get_logger().warning('Ignored direct command while busy; use /cra/intent_raw.')
            return
        self.intent = msg
        self.state = 'EXECUTING'
        self.progress = 0.0
        self.started = time.monotonic()
        self.pending_error = None
        self.origin = self.position
        try:
            if msg.intent_type != 'move_forward' or len(msg.args) != 1:
                raise ValueError('Expected move_forward with one distance argument in metres')
            self.target = float(msg.args[0])
            if not math.isfinite(self.target) or not 0.1 <= self.target <= 2.0:
                raise ValueError('Distance must be finite and between 0.1 and 2.0 metres')
            if self.position is None or self.started - self.last_odom > 1.0:
                raise ValueError('No fresh Gazebo odometry; start the simulation first')
            self.detail = f'Driving forward {self.target:.2f} m'
        except ValueError as error:
            self.pending_error = str(error)
            self.detail = 'Validating command'
        # Every dispatched request has an EXECUTING transition before its result.
        self.publish_state()

    def stop(self):
        self.command.publish(Twist())

    def finish(self, state, detail):
        self.stop()
        self.state = state
        self.detail = detail
        self.get_logger().info(f'{state}: {detail}')

    def tick(self):
        if self.state == 'EXECUTING':
            now = time.monotonic()
            if self.pending_error:
                self.finish('ERROR', self.pending_error)
            elif now - self.last_odom > 1.0:
                self.finish('ERROR', 'Odometry lost or simulation paused')
            elif now - self.started > 25.0:
                self.finish('ERROR', 'Motion timed out')
            else:
                distance = math.dist(self.origin, self.position)
                self.progress = min(distance / self.target, 1.0)
                if distance >= self.target - 0.015:
                    self.progress = 1.0
                    self.finish('DONE', f'Travelled {distance:.3f} m (target {self.target:.3f} m)')
                else:
                    velocity = Twist()
                    velocity.linear.x = min(0.2, max(0.05, self.target - distance))
                    self.command.publish(velocity)
        else:
            self.stop()
        self.publish_state()

    def publish_state(self):
        self.feedback.publish(ExecutionState(
            state=self.state, intent_type=self.intent.intent_type,
            args=list(self.intent.args), progress=float(self.progress), detail=self.detail))


def main(args=None):
    rclpy.init(args=args)
    node = GazeboExecutor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.stop()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
