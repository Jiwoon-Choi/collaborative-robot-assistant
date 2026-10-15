#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
source /opt/ros/humble/setup.bash
source install/setup.bash
exec ros2 topic pub --once /cra/intent_raw cra_msgs/msg/Intent "{intent_type: move_forward, args: ['0.5']}"
