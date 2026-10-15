#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
source /opt/ros/humble/setup.bash
source install/setup.bash
exec ros2 launch cra_gazebo cra_gazebo.launch.py "$@"
