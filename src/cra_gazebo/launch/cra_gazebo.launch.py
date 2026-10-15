"""Launch a self-contained mobile base, bridge, FSM, and drive skill."""
from pathlib import Path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    world = str(Path(get_package_share_directory('cra_gazebo')) / 'worlds' / 'cra_world.sdf')
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true'),
        ExecuteProcess(cmd=['ign', 'gazebo', '-r', '-s', world], output='screen'),
        ExecuteProcess(cmd=['ign', 'gazebo', '-g', '--render-engine', 'ogre'], output='screen',
                       condition=IfCondition(LaunchConfiguration('gui'))),
        Node(package='ros_gz_bridge', executable='parameter_bridge', arguments=[
            '/cra/base/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/cra/base/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
        ], output='screen'),
        Node(package='cra_fsm', executable='fsm_node', output='screen'),
        Node(package='cra_gazebo', executable='executor_node', output='screen'),
    ])
