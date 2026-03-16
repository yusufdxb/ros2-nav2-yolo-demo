"""
Nav2 + YOLOv8 Demo — Master Launch File
Launches: Gazebo world, TurtleBot3, Nav2, YOLO detector, navigator node.

Usage:
  ros2 launch nav2_yolo_bringup demo_launch.py
  ros2 launch nav2_yolo_bringup demo_launch.py target_class:=chair
"""

import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    target_class = LaunchConfiguration("target_class")
    use_rviz = LaunchConfiguration("use_rviz")

    declare_target = DeclareLaunchArgument(
        "target_class",
        default_value="person",
        description="YOLO class name to navigate toward (e.g. person, chair, bottle)",
    )
    declare_rviz = DeclareLaunchArgument(
        "use_rviz",
        default_value="true",
        description="Launch RViz2 for visualization",
    )

    # Set TurtleBot3 model
    set_tb3_model = SetEnvironmentVariable("TURTLEBOT3_MODEL", "waffle_pi")

    # ── Gazebo world ────────────────────────────────────────────────────
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("gazebo_ros"), "launch", "gazebo.launch.py"
            ])
        ]),
        launch_arguments={
            "world": PathJoinSubstitution([
                FindPackageShare("nav2_yolo_bringup"), "worlds", "demo_world.world"
            ]),
            "verbose": "false",
        }.items(),
    )

    # ── TurtleBot3 spawn ─────────────────────────────────────────────────
    tb3_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("turtlebot3_gazebo"),
                "launch", "spawn_turtlebot3.launch.py"
            ])
        ]),
        launch_arguments={
            "x_pose": "0.0",
            "y_pose": "0.0",
        }.items(),
    )

    # ── Nav2 ──────────────────────────────────────────────────────────────
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("nav2_bringup"),
                "launch", "navigation_launch.py"
            ])
        ]),
        launch_arguments={
            "use_sim_time": "true",
            "params_file": PathJoinSubstitution([
                FindPackageShare("nav2_yolo_bringup"), "config", "nav2_params.yaml"
            ]),
        }.items(),
    )

    # ── SLAM (map building) ───────────────────────────────────────────────
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("slam_toolbox"),
                "launch", "online_async_launch.py"
            ])
        ]),
        launch_arguments={"use_sim_time": "true"}.items(),
    )

    # ── YOLO Detector ─────────────────────────────────────────────────────
    detector_node = Node(
        package="nav2_yolo_detector",
        executable="detector_node",
        name="detector_node",
        parameters=[
            {"model_path": "yolov8n.pt"},
            {"confidence_threshold": 0.45},
            {"max_depth_m": 10.0},
            {"publish_visualization": True},
            {"use_sim_time": True},
        ],
        remappings=[
            ("/camera/image_raw", "/camera/image_raw"),
            ("/camera/depth/image_raw", "/camera/depth/image_raw"),
        ],
        output="screen",
    )

    # ── Navigator ─────────────────────────────────────────────────────────
    navigator_node = Node(
        package="nav2_yolo_navigator",
        executable="navigator_node",
        name="navigator_node",
        parameters=[
            {"target_class": target_class},
            {"min_confidence": 0.5},
            {"goal_offset_m": 0.8},
            {"replan_distance_m": 0.5},
            {"use_sim_time": True},
        ],
        output="screen",
    )

    # ── RViz2 ─────────────────────────────────────────────────────────────
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=[
            "-d", PathJoinSubstitution([
                FindPackageShare("nav2_yolo_bringup"), "rviz", "demo.rviz"
            ])
        ],
        output="screen",
        condition=__import__("launch.conditions", fromlist=["IfCondition"]).IfCondition(use_rviz),
    )

    return LaunchDescription([
        declare_target,
        declare_rviz,
        set_tb3_model,
        gazebo_launch,
        tb3_launch,
        slam_launch,
        nav2_launch,
        detector_node,
        navigator_node,
        rviz_node,
    ])
