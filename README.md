# ROS 2 Nav2 + YOLOv8 Object Navigation Demo 🤖

A Gazebo simulation where a mobile robot uses **YOLOv8** to detect objects and **Nav2** to autonomously navigate toward them. No real hardware needed — runs entirely in simulation.

[![Demo](https://img.shields.io/badge/▶_Watch_Demo-YouTube-red)](https://youtube.com)
![ROS2](https://img.shields.io/badge/ROS_2-Humble-blue)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## What It Does

```
Camera feed → YOLOv8 detection → 3D position estimate → Nav2 goal → Robot navigates to object
```

1. Robot spawns in a Gazebo world with objects scattered around
2. YOLOv8 detects objects in the camera stream and estimates their 3D position using depth
3. The user selects a target class (e.g. "person", "chair", "bottle")
4. The system sends a Nav2 goal to the object's estimated map location
5. The robot navigates there autonomously, avoiding obstacles

---

## Demo

> *Add a GIF here — record your Gazebo sim with `ros2 run rqt_image_view rqt_image_view` + screen capture*

---

## Why This Project

This demo directly combines two core robotics skills:

| Skill | Component |
|---|---|
| **Autonomous navigation** | Nav2 — path planning, obstacle avoidance, costmaps |
| **Object perception** | YOLOv8 — real-time detection + depth-based 3D localization |

Together they form the foundation of any mobile robot that needs to act on what it sees — from warehouse robots to assistive systems.

---

## Prerequisites

```bash
# ROS 2 Humble
sudo apt install ros-humble-desktop ros-humble-nav2-bringup ros-humble-turtlebot3*

# Python deps
pip install ultralytics opencv-python numpy

# Gazebo
sudo apt install ros-humble-gazebo-ros-pkgs
```

---

## Quickstart

```bash
# Clone
git clone https://github.com/yusufdxb/ros2-nav2-yolo-demo.git
cd ros2-nav2-yolo-demo
colcon build --symlink-install
source install/setup.bash

# Export TurtleBot3 model
export TURTLEBOT3_MODEL=waffle_pi

# Launch Gazebo world + Nav2 + YOLO detector
ros2 launch nav2_yolo_bringup demo_launch.py

# In a new terminal — navigate to a detected object
ros2 run nav2_yolo_navigator navigator_node --ros-args -p target_class:=person
```

---

## Package Structure

```
ros2-nav2-yolo-demo/
├── nav2_yolo_bringup/          # Launch files
│   └── launch/
│       └── demo_launch.py
├── nav2_yolo_detector/         # YOLOv8 detection + 3D localization node
│   └── nav2_yolo_detector/
│       └── detector_node.py
├── nav2_yolo_navigator/        # Goal publisher — sends Nav2 goals to detections
│   └── nav2_yolo_navigator/
│       └── navigator_node.py
├── nav2_yolo_msgs/             # Custom messages
│   └── msg/
│       ├── DetectedObject.msg
│       └── DetectedObjectArray.msg
├── config/
│   └── nav2_params.yaml        # Nav2 configuration
└── worlds/
    └── demo_world.sdf          # Gazebo world with objects
```

---

## Node Graph

```
/camera/image_raw ──────────────► [detector_node]
/camera/depth/image_raw ─────────►     │
                                        │ /detected_objects
                                        ▼
                              [navigator_node]
                                        │
                                        │ /goal_pose
                                        ▼
                                  [Nav2 stack]
                                        │
                                        ▼
                              [TurtleBot3 in Gazebo]
```

---

## Configuration

Set your target object class at launch:

```bash
# Navigate to a person
ros2 run nav2_yolo_navigator navigator_node --ros-args -p target_class:=person

# Navigate to a chair
ros2 run nav2_yolo_navigator navigator_node --ros-args -p target_class:=chair

# Navigate to a bottle
ros2 run nav2_yolo_navigator navigator_node --ros-args -p target_class:=bottle
```

YOLO confidence threshold and other parameters are in `config/nav2_params.yaml`.

---

## Relationship to GO2 Thesis

This demo isolates the **Nav2 + YOLOv8** pipeline from my [GO2 Seeing-Eye Dog](https://github.com/yusufdxb/GO2-seeing-eye-dog) thesis project. The GO2 system extends this with:

- Legged robot (Unitree GO2) instead of wheeled TurtleBot
- Microphone array + sound-source localization
- Audio-visual intent grounding
- Safety perception (stairs, curbs, narrow passages)
- Whisper voice command interface

---

## Author

**Yusuf Guenena** | M.S. Robotics Engineering, Wayne State University
[LinkedIn](https://www.linkedin.com/in/yusuf-guenena) · [GitHub](https://github.com/yusufdxb)
