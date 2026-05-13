# ROS 2 Nav2 + YOLOv8 Object Navigation Demo

> **Status: archived reference implementation.** A clean, buildable, hardware-tested successor lives at [`yusufdxb/ros2-go2-nav2-yolo`](https://github.com/yusufdxb/ros2-go2-nav2-yolo). Use that for any actual ROS 2 Nav2 + YOLO work on the GO2 stack. This repo is preserved for historical / portfolio reference only.

A Gazebo simulation sketch where a mobile robot uses **YOLOv8** to detect objects and **Nav2** to autonomously navigate toward them. Intended to isolate the perception + planning pipeline before porting it to the Unitree GO2 platform.

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

## Why This Project

This demo directly combines two core robotics skills:

| Skill | Component |
|---|---|
| **Autonomous navigation** | Nav2: path planning, obstacle avoidance, costmaps |
| **Object perception** | YOLOv8: real-time detection plus depth-based 3D localization |

Together they form the foundation of any mobile robot that needs to act on what it sees, from warehouse robots to assistive systems.

---

## Quickstart

This is a reference dump and not buildable as-is (no `package.xml` / `setup.py`). For a buildable, tested version of this stack, see [`yusufdxb/ros2-go2-nav2-yolo`](https://github.com/yusufdxb/ros2-go2-nav2-yolo).

---

## Package Structure

See `nav2_yolo_bringup/` for the launch, config, and Gazebo world layout. The four ROS 2 packages in this repo are:

- `nav2_yolo_bringup/` (launch files, Nav2 params, Gazebo world)
- `nav2_yolo_detector/` (YOLOv8 detection + 3D localization node)
- `nav2_yolo_navigator/` (goal publisher, sends Nav2 goals to detections)
- `nav2_yolo_msgs/` (custom messages: `DetectedObject`, `DetectedObjectArray`)

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

Target object class is set as a ROS 2 parameter on the navigator node (e.g. `target_class:=person`, `target_class:=chair`, `target_class:=bottle`). YOLO confidence threshold and Nav2 tuning live in `nav2_yolo_bringup/config/nav2_params.yaml`.

---

## Relationship to GO2 Thesis

This demo isolates the **Nav2 + YOLOv8** pipeline from my [GO2 Seeing-Eye Dog](https://github.com/yusufdxb/GO2-seeing-eye-dog) thesis project. The GO2 system extends this with:

- Legged robot (Unitree GO2) instead of wheeled TurtleBot
- Microphone array and sound-source localization
- Audio-visual intent grounding
- Safety perception (stairs, curbs, narrow passages)
- Whisper voice command interface

For the buildable, hardware-tested Nav2 + YOLO core that grew out of this sketch, see [`yusufdxb/ros2-go2-nav2-yolo`](https://github.com/yusufdxb/ros2-go2-nav2-yolo).

---

## Author

**Yusuf Guenena** | M.S. Robotics Engineering, Wayne State University
[LinkedIn](https://www.linkedin.com/in/yusuf-guenena) · [GitHub](https://github.com/yusufdxb)
