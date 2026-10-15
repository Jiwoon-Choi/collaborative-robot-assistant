"""Send a three-command burst and verify ordered dispatch and completion."""
import time
import rclpy
from cra_msgs.msg import Intent, ExecutionState


def main():
    rclpy.init()
    node = rclpy.create_node('cra_demo_client')
    expected = ['demo_greet', 'demo_wait', 'demo_finish']
    dispatched, completed = [], []
    ready = False
    sent = False
    last = None

    def command(msg):
        if sent:
            dispatched.append(msg.intent_type)

    def feedback(msg):
        nonlocal ready, last
        ready = True
        if not sent:
            return
        key = (msg.intent_type, msg.state)
        if key != last:
            print(f'{msg.intent_type}: {msg.state} ({msg.progress:.0%})', flush=True)
            last = key
        if msg.state == 'DONE' and msg.intent_type not in completed:
            completed.append(msg.intent_type)

    publisher = node.create_publisher(Intent, '/cra/intent_raw', 10)
    node.create_subscription(Intent, '/cra/intent', command, 10)
    node.create_subscription(ExecutionState, '/cra/execution_state', feedback, 10)
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
            if ready and publisher.get_subscription_count() and node.count_publishers('/cra/intent'):
                break
        else:
            raise RuntimeError('CRA nodes not ready. Start bash scripts/run_demo.sh first.')
        sent = True
        for name in expected:
            publisher.publish(Intent(intent_type=name, args=[]))
        print('Sent three mock commands. Expected: one executing, two queued.', flush=True)
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline and len(completed) < len(expected):
            rclpy.spin_once(node, timeout_sec=0.1)
        if dispatched != expected or completed != expected:
            raise RuntimeError(f'Unexpected result: dispatched={dispatched}, completed={completed}')
        print('PASS: all three commands dispatched and completed in order.', flush=True)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
