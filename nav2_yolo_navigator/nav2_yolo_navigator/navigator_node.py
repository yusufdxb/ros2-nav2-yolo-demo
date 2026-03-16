#!/usr/bin/env python3
"""
Nav2 + YOLOv8 Demo — Navigator Node
Subscribes to detected objects, filters by target class,
transforms the 3D position from camera frame to map frame,
and sends a Nav2 NavigateToPose action goal.

Usage:
  ros2 run nav2_yolo_navigator navigator_node --ros-args -p target_class:=person
"""

import math
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.duration import Duration

from geometry_msgs.msg import PoseStamped, TransformStamped
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import String
import tf2_ros
import tf2_geometry_msgs

from nav2_yolo_msgs.msg import DetectedObjectArray


class NavigatorNode(Node):
    def __init__(self):
        super().__init__("navigator_node")

        self.declare_parameter("target_class", "person")
        self.declare_parameter("min_confidence", 0.5)
        self.declare_parameter("goal_offset_m", 0.8)       # Stop this far from the object
        self.declare_parameter("replan_distance_m", 0.5)   # Re-send goal if object moves this much
        self.declare_parameter("nav_timeout_sec", 30.0)

        self.target_class = self.get_parameter("target_class").value
        self.min_conf = self.get_parameter("min_confidence").value
        self.goal_offset = self.get_parameter("goal_offset_m").value
        self.replan_dist = self.get_parameter("replan_distance_m").value
        self.nav_timeout = self.get_parameter("nav_timeout_sec").value

        # TF
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Nav2 action client
        self.nav_client = ActionClient(self, NavigateToPose, "navigate_to_pose")

        # State
        self.current_goal_pose = None
        self.nav_active = False
        self._goal_handle = None

        # Subscribers
        self.detections_sub = self.create_subscription(
            DetectedObjectArray, "/detected_objects", self.detections_callback, 10
        )

        # Publishers
        self.status_pub = self.create_publisher(String, "/navigator/status", 10)

        self.get_logger().info(
            f"NavigatorNode ready. Target class: '{self.target_class}'"
        )
        self._publish_status("WAITING_FOR_DETECTION")

    # ── Detection callback ──────────────────────────────────────────────

    def detections_callback(self, msg: DetectedObjectArray):
        # Filter for target class, pick highest-confidence detection
        candidates = [
            obj for obj in msg.objects
            if obj.class_name == self.target_class and obj.confidence >= self.min_conf
        ]

        if not candidates:
            return

        best = max(candidates, key=lambda o: o.confidence)

        # Build PoseStamped in camera frame
        cam_pose = PoseStamped()
        cam_pose.header = msg.header
        cam_pose.pose.position.x = best.position.x
        cam_pose.pose.position.y = best.position.y
        cam_pose.pose.position.z = best.position.z
        cam_pose.pose.orientation.w = 1.0

        # Transform to map frame
        try:
            map_pose = self.tf_buffer.transform(
                cam_pose, "map", timeout=Duration(seconds=0.2)
            )
        except Exception as e:
            self.get_logger().warn(f"TF transform failed: {e}")
            return

        # Apply approach offset — stop goal_offset_m in front of the object
        yaw = math.atan2(map_pose.pose.position.y, map_pose.pose.position.x)
        map_pose.pose.position.x -= self.goal_offset * math.cos(yaw)
        map_pose.pose.position.y -= self.goal_offset * math.sin(yaw)

        # Face the object
        map_pose.pose.orientation.z = math.sin(yaw / 2.0)
        map_pose.pose.orientation.w = math.cos(yaw / 2.0)

        # Check if we need to replan (object moved significantly)
        if self.current_goal_pose is not None and self.nav_active:
            dx = map_pose.pose.position.x - self.current_goal_pose.pose.position.x
            dy = map_pose.pose.position.y - self.current_goal_pose.pose.position.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < self.replan_dist:
                return  # Close enough — keep current goal
            else:
                self.get_logger().info(
                    f"Object moved {dist:.2f}m — replanning"
                )
                self._cancel_current_goal()

        self.current_goal_pose = map_pose
        self._send_nav_goal(map_pose)

    # ── Nav2 goal management ────────────────────────────────────────────

    def _send_nav_goal(self, pose: PoseStamped):
        if not self.nav_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().warn("Nav2 action server not available")
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose

        self.get_logger().info(
            f"Sending goal to '{self.target_class}' at "
            f"({pose.pose.position.x:.2f}, {pose.pose.position.y:.2f})"
        )
        self._publish_status(f"NAVIGATING_TO_{self.target_class.upper()}")

        send_future = self.nav_client.send_goal_async(
            goal_msg,
            feedback_callback=self._feedback_callback,
        )
        send_future.add_done_callback(self._goal_accepted_callback)
        self.nav_active = True

    def _goal_accepted_callback(self, future):
        self._goal_handle = future.result()
        if not self._goal_handle.accepted:
            self.get_logger().warn("Nav2 goal rejected")
            self.nav_active = False
            self._publish_status("GOAL_REJECTED")
            return

        result_future = self._goal_handle.get_result_async()
        result_future.add_done_callback(self._result_callback)

    def _feedback_callback(self, feedback_msg):
        dist = feedback_msg.feedback.distance_remaining
        self.get_logger().debug(f"Distance remaining: {dist:.2f}m")

    def _result_callback(self, future):
        result = future.result().result
        self.nav_active = False
        self.current_goal_pose = None
        self.get_logger().info(
            f"Navigation complete. Result code: {future.result().status}"
        )
        self._publish_status("ARRIVED")

    def _cancel_current_goal(self):
        if self._goal_handle is not None:
            self._goal_handle.cancel_goal_async()
        self.nav_active = False

    def _publish_status(self, status: str):
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = NavigatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
