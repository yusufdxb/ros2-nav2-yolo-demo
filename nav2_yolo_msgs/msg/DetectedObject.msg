# nav2_yolo_msgs/msg/DetectedObject.msg
# A single YOLO-detected object with 3D position

string class_name         # COCO class label (e.g. "person", "chair")
int32 class_id            # COCO class ID
float32 confidence        # Detection confidence [0, 1]
geometry_msgs/Point position  # 3D position in camera frame (meters)
int32 bbox_x1
int32 bbox_y1
int32 bbox_x2
int32 bbox_y2
