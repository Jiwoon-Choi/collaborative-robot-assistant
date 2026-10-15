#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
source /opt/ros/humble/setup.bash
if [ ! -f install/setup.bash ]; then
    echo 'Build first: source /opt/ros/humble/setup.bash && colcon build'
    exit 1
fi
source install/setup.bash
exec ros2 launch "$PWD/launch/cra_demo.launch.py"
