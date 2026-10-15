"""Check invalid-command recovery, queued motion, distance, and stopping."""
import math
import time
import rclpy
from nav_msgs.msg import Odometry
from cra_msgs.msg import Intent, ExecutionState

rclpy.init()
node = rclpy.create_node('cra_motion_check')
position = None
outcomes = []
states = []
def odom(msg):
    global position
    position = (msg.pose.pose.position.x, msg.pose.pose.position.y)
def feedback(msg):
    key = (msg.state, tuple(msg.args))
    if not states or states[-1] != key:
        states.append(key)
        print(msg.state, list(msg.args), msg.detail, flush=True)
        if msg.state in ('DONE', 'ERROR'):
            outcomes.append((msg.state, tuple(msg.args), position))
node.create_subscription(Odometry, '/cra/base/odom', odom, 10)
node.create_subscription(ExecutionState, '/cra/execution_state', feedback, 10)
publisher = node.create_publisher(Intent, '/cra/intent_raw', 10)
def spin_until(condition, seconds):
    deadline = time.monotonic() + seconds
    while not condition() and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.05)
    assert condition(), 'Timed out'
try:
    spin_until(lambda: position is not None and bool(states) and publisher.get_subscription_count() > 0, 25)
    start = position
    for distance in ['nan', '0.5', '0.3']:
        publisher.publish(Intent(intent_type='move_forward', args=[distance]))
    spin_until(lambda: len(outcomes) == 3, 35)
    assert [(s, a) for s, a, p in outcomes] == [('ERROR', ('nan',)), ('DONE', ('0.5',)), ('DONE', ('0.3',))], outcomes
    first = math.dist(start, outcomes[1][2])
    second = math.dist(outcomes[1][2], outcomes[2][2])
    assert 0.46 <= first <= 0.55, first
    assert 0.26 <= second <= 0.35, second
    stop_position = position
    until = time.monotonic() + 1
    while time.monotonic() < until:
        rclpy.spin_once(node, timeout_sec=0.05)
    drift = math.dist(stop_position, position)
    assert drift < 0.03, drift
    print(f'PASS: invalid input rejected, queued distances {first:.3f} m and {second:.3f} m, stop drift {drift:.4f} m', flush=True)
finally:
    node.destroy_node()
    rclpy.try_shutdown()
