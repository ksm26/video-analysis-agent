import cv2
from ultralytics import YOLO
import os

class VideoAnalyzer:
    def __init__(self, video_path, model_path="models/yolov8s.pt"):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"YOLOv8 model not found at {model_path}")

        self.model = YOLO(model_path)

    def analyze_for_action(self, action_id):
        """
        Detect presence of UI element/action based on action_id mapping to UI label.
        """
        print(f"[INFO] Searching for action: {action_id} in video {self.video_path}")

        label_to_detect = self._map_action_to_label(action_id)
        if not label_to_detect:
            print(f"[WARN] No label mapping found for action: {action_id}")
            return False, None

        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        for _ in range(frame_count):
            ret, frame = self.cap.read()
            if not ret:
                break

            detections = self.model(frame)

            for det in detections:
                for box in det.boxes:
                    cls_name = det.names[int(box.cls)]
                    if cls_name.lower() == label_to_detect.lower():
                        timestamp = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                        return True, round(timestamp, 2)

        return False, None

    def _map_action_to_label(self, action_id):
        """
        Maps abstract action_id to detectable UI label in the YOLO model.
        Example: "click_login" => "login_button"
        """
        mappings = {
            "click_login": "login_button",
            "enter_password": "password_field",
            "submit_form": "submit_button"
        }
        return mappings.get(action_id.lower())
