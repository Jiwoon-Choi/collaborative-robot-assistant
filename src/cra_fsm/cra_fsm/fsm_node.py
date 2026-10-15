#!/usr/bin/env python3

from collections import deque
import rclpy
from rclpy.node import Node

from cra_msgs.msg import Intent, ExecutionState


class CraFsmNode(Node):
    """
    FSM v1:
      - subscribes: /cra/intent_raw (Intent)
      - publishes:  /cra/intent     (Intent)
      - subscribes: /cra/execution_state (ExecutionState)

    Behavior:
      - If not busy, forward immediately.
      - If busy, queue raw intents.
      - When execution becomes DONE (or ERROR), dispatch next queued intent.
    """

    def __init__(self):
        super().__init__("cra_fsm")

        self.sub_raw = self.create_subscription(
            Intent, "/cra/intent_raw", self.on_intent_raw, 10
        )

        self.sub_state = self.create_subscription(
            ExecutionState, "/cra/execution_state", self.on_execution_state, 10
        )

        self.pub_intent = self.create_publisher(
            Intent, "/cra/intent", 10
        )

        # Busy means: we have dispatched a command and are waiting for completion feedback
        self.busy = False

        # FIFO queue for incoming raw intents while busy
        self.queue = deque()

        # Track last known executor state string (for edge detection)
        self.last_exec_state = ""

        self.get_logger().info(
            "cra_fsm v1 started. Gating + queue enabled: /cra/intent_raw -> /cra/intent"
        )

    def on_intent_raw(self, msg: Intent):
        if not self.busy:
            self.dispatch_intent(msg, reason="idle")
            self.busy = True
        else:
            self.queue.append(msg)
            self.get_logger().info(
                f"Busy. Queued intent_raw: intent_type='{msg.intent_type}', "
                f"args={list(msg.args)} (queue_size={len(self.queue)})"
            )

    def on_execution_state(self, msg: ExecutionState):
        # We only need coarse transitions for v1
        state = msg.state

        # Ignore duplicate states to reduce spam
        if state == self.last_exec_state:
            return
        self.last_exec_state = state

        self.get_logger().info(
            f"Executor state changed: state='{state}', progress={msg.progress:.2f}, detail='{msg.detail}'"
        )

        # Treat DONE and ERROR as "not busy anymore"
        if state in ("DONE", "ERROR"):
            if self.busy:
                self.busy = False

            # If we have queued intents, dispatch the next one
            if self.queue:
                next_intent = self.queue.popleft()
                self.dispatch_intent(next_intent, reason=f"executor_{state.lower()}")
                self.busy = True

    def dispatch_intent(self, msg: Intent, reason: str):
        self.pub_intent.publish(msg)
        self.get_logger().info(
            f"Dispatched ({reason}): intent_type='{msg.intent_type}', args={list(msg.args)}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = CraFsmNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
