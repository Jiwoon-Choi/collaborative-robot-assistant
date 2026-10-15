"""Launch the recovered CRA decision layer and timed mock executor."""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='cra_fsm', executable='fsm_node', output='screen'),
        Node(package='cra_execution_sim', executable='executor_node', output='screen'),
    ])
