#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from cra_msgs.msg import Intent, ExecutionState


class ExecutorSimNode(Node):
    def __init__(self):
        super().__init__("cra_executor_sim")

        self.intent_sub = self.create_subscription(
            Intent,
            "/cra/intent",
            self.on_intent,
            10
        )

        self.state_pub = self.create_publisher(
            ExecutionState,
            "/cra/execution_state",
            10
        )

        self.current_state = "IDLE"
        self.active_intent_type = ""
        self.active_args = []
        self.exec_ticks_total = 20          # 20 ticks at 10 Hz = ~2 seconds
        self.exec_ticks_remaining = 0
        self.detail = "Idle"

        self.timer = self.create_timer(0.1, self.on_timer)

        self.get_logger().info("cra_executor_sim started. Waiting for /cra/intent ...")

    def on_intent(self, msg: Intent):
        self.active_intent_type = msg.intent_type
        self.active_args = list(msg.args)

        self.current_state = "EXECUTING"
        self.exec_ticks_remaining = self.exec_ticks_total
        self.detail = "Executing intent in simulation"

        self.get_logger().info(
            f"Received intent: intent_type='{self.active_intent_type}', args={self.active_args}"
        )

        self.publish_state()  # immediate update

    def on_timer(self):
        if self.current_state == "EXECUTING":
            self.exec_ticks_remaining -= 1
            if self.exec_ticks_remaining <= 0:
                self.current_state = "DONE"
                self.detail = "Execution finished"

        self.publish_state()

    def publish_state(self):
        msg = ExecutionState()
        msg.state = self.current_state
        msg.intent_type = self.active_intent_type
        msg.args = self.active_args

        if self.current_state == "EXECUTING" and self.exec_ticks_total > 0:
            done = self.exec_ticks_total - self.exec_ticks_remaining
            msg.progress = float(done) / float(self.exec_ticks_total)
        elif self.current_state == "DONE":
            msg.progress = 1.0
        else:
            msg.progress = 0.0

        msg.detail = self.detail
        self.state_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ExecutorSimNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
