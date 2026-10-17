# CRA Gazebo mobile-base milestone

## What works

Typed Intent -> existing queued FSM -> distance-based executor -> ROS/Gazebo bridge -> differential-drive robot -> odometry -> execution feedback.

This is direct straight-line control in an empty world. It is not Nav2 navigation, obstacle avoidance, arm manipulation, perception, or voice control.

## Run in Ubuntu 22.04

Stop the old mock demo before starting this one: both executors use /cra/intent and /cra/execution_state. Run only one CRA launch at a time.

Terminal 1:

```bash
cd ~/cra_ws
bash scripts/run_gazebo.sh
```

Gazebo starts running automatically. The blue mobile base is near the world origin. The launch uses Ogre rendering because the default Ogre 2 renderer threw a graphics exception under this PC's WSLg setup.

Terminal 2:

```bash
cd ~/cra_ws
bash scripts/move_forward.sh
```

This requests 0.5 meters forward. Watch the robot and the first terminal's DONE message. Repeat to request another move. Ctrl+C in Terminal 1 stops the launch.

For custom distances, from a sourced workspace:

```bash
source /opt/ros/humble/setup.bash
source ~/cra_ws/install/setup.bash
ros2 topic pub --once /cra/intent_raw cra_msgs/msg/Intent "{intent_type: move_forward, args: ['1.0']}"
```

Allowed distances: 0.1–2.0m. Invalid requests report ERROR and the FSM continues to the next queued request. Validation currently lives in the Gazebo executor, not the FSM.

## Verification

With a fresh Gazebo launch (no other publishers), run:

```bash
cd ~/cra_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
python3 scripts/check_gazebo_motion.py
```

It queues an invalid NaN distance followed by 0.5m and 0.3m moves, verifies ERROR/DONE/DONE, checks odometry displacement, and checks stopping drift. The headless integration run measured 0.486m and 0.285m; one-second stopping drift was 0.0012m. Distance completion uses a 0.015m tolerance. These are odometry measurements, not independently measured ground-truth pose.

To run without a window: `bash scripts/run_gazebo.sh gui:=false`.

## Installation/build

Already installed on this PC:

```bash
sudo apt-get update
sudo apt-get install ros-humble-ros-gz ignition-fortress
source /opt/ros/humble/setup.bash
colcon build
```

Official compatibility: https://gazebosim.org/docs/fortress/ros_installation/
Rendering fallback: https://gazebosim.org/docs/fortress/troubleshooting/

## Limits

- Max commanded speed 0.2m/s; motion times out after 25 seconds of wall time.
- Missing/stale odometry causes ERROR; pausing the simulator during motion can trigger this.
- Distance is displacement from the starting odometry position, without heading correction or obstacle handling.
- Direct commands received while executing are ignored; send requests via /cra/intent_raw.
- No command IDs, cancellation, executor-crash watchdog in the simulator, or restart recovery. For simulation only.
- Existing FSM's ERROR policy continues the queue; this is a demo policy, not a hardware safety policy.
