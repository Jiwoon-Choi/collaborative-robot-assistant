# CRA project status — October 17, 2026

## Current milestone

CRA supports typed forward-motion requests for a differential-drive
mobile robot in Gazebo Fortress.

The implemented flow is:

Intent request → FSM queue → Gazebo drive executor → velocity command
→ simulated robot → odometry → execution feedback → FSM

The original timed mock executor remains available as a separate demo.
Run only one CRA demo at a time.

## Environment

- Ubuntu 22.04 through WSL 2
- ROS 2 Humble
- Gazebo Fortress with the ROS–Gazebo bridge
- Ogre rendering fallback for this PC's WSL graphics environment

## Implemented behavior

- FIFO command queue and one-at-a-time dispatch.
- move_forward requests with distances from 0.1 to 2.0 metres.
- Distance validation in the Gazebo executor.
- Odometry-based progress and completion with a 0.015 m tolerance.
- Motion timeout and stale-odometry detection.
- ExecutionState feedback, including EXECUTING, DONE, and ERROR.
- Queue advancement after DONE or ERROR.

## Verification completed

Automated checks:
- All four packages built successfully.
- Gazebo world description passed SDF validation.
- Invalid NaN distance was rejected.
- Queued 0.5 m and 0.3 m requests completed in order.
- Odometry measured approximately 0.486 m and 0.285 m.
- Additional displacement during a one-second stopping check was 0.0012 m.
- Headless launch processes shut down cleanly.

Manual checks completed by the project author:
- Gazebo displays the robot moving and stopping.
- Velocity commands decrease near the target and become zero afterward.
- Odometry changes during movement.
- A second request waits in the queue until the first completes.
- A negative-distance request produces ERROR, followed by successful
  execution of a valid request.

These checks establish the demonstrated behavior, not exhaustive
validation of every failure mode. Reported distances are odometry-based,
not independently verified ground-truth measurements.

## Current limitations

- Forward motion only; no heading correction or obstacle avoidance.
- No voice input, language parsing, Nav2, perception, or arm manipulation.
- No command IDs, cancellation, queue limit, or restart recovery.
- The FSM distinguishes feedback by state transitions rather than
  command identity.
- Continuing the queue after ERROR is the current demo policy.
- Intended for simulation; hardware safety behavior is not implemented.

## Next deliverables

1. Update the README to lead with the Gazebo demonstration.
2. Record a short demonstration video.
3. Complete the publication review and publish the repository to GitHub.

## Development history

Recovered the existing FSM v1 and timed mock executor, preserved them
in Git, then added the Gazebo mobile-base integration.

Implementation and documentation were developed with AI assistance.
The project author has manually inspected and exercised the demo.
