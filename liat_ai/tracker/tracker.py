import os
import pickle
import cv2
from ultralytics import YOLO
import supervision as sv
import numpy as np
from utils import get_center_of_bbox, get_bbox_width

class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def get_object_tracks(self, video_path, tracker_config, read_from_stub=False, stub_path=None):
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path,'rb') as f:
                tracks = pickle.load(f)
            print(f"Loaded tracks from stub: {stub_path}")
            return tracks

        print(f"Performing tracking on {video_path}...")

        # Get total number of frames for progress display
        # We will rely on verbose=True for progress output from ultralytics
        # Use ultralytics track method which handles both detection and tracking
        results = self.model.track(source=video_path, tracker=tracker_config, persist=True, stream=True, verbose=True)

        tracks = {
            "players": [],
            "referees": [],
            "ball": []
        }

        for frame_num, result in enumerate(results):
            # Custom Print progress if verbose=False
            # print(f"Processing frame {frame_num + 1} / {total_frames}", end='\r')

            cls_names = result.names
            cls_names_inv = {v:k for k, v in cls_names.items()}

            # Convert to Supervision Detection Format
            detection_supervision = sv.Detections.from_ultralytics(result)

            # Convert GoalKeeper to Player Object
            for object_ind, class_id in enumerate(detection_supervision.class_id):
                if cls_names[class_id] == "goalkeeper":
                    detection_supervision.class_id[object_ind] = cls_names_inv["player"]

            # Process tracked objects
            players_in_frame = {}
            referees_in_frame = {}
            ball_in_frame = {}

            if result.boxes.id is not None: # Check if tracking results are available
                for bbox, confidence, class_id, tracker_id in zip(result.boxes.xyxy.tolist(), result.boxes.conf.tolist(), result.boxes.cls.tolist(), result.boxes.id.tolist()):
                    class_name = cls_names[class_id]

                    if class_name == 'player':
                        players_in_frame[tracker_id] = {"bbox": bbox, "confidence": confidence}
                    elif class_name == 'referee':
                        referees_in_frame[tracker_id] = {"bbox": bbox, "confidence": confidence}

            # Process ball detections (ball does not have track_id)
            for bbox, confidence, class_id in zip(detection_supervision.xyxy.tolist(), detection_supervision.confidence.tolist(), detection_supervision.class_id.tolist()):
                class_name = cls_names[class_id]
                if class_name == 'ball':
                    # Assuming only one ball, assign a fixed ID like 1
                    ball_in_frame[1] = {"bbox": bbox, "confidence": confidence}


            tracks["players"].append(players_in_frame)
            tracks["referees"].append(referees_in_frame)
            tracks["ball"].append(ball_in_frame)


        # print("\nTracking complete.")

        if stub_path is not None:
            print(f"Saving tracks to stub: {stub_path}")
            # Ensure the directory exists
            os.makedirs(os.path.dirname(stub_path), exist_ok=True)
            with open(stub_path,'wb') as f:
                pickle.dump(tracks,f)
            print("Stub saved.")


        return tracks

    def draw_ellipse(self, frame, bbox, color, track_id=None):
        y2 = int(bbox[3])
        x_center, _ = get_center_of_bbox(bbox)
        width = get_bbox_width(bbox)

        cv2.ellipse(
            frame,
            center=(x_center, y2),
            axes=(int(width), int(0.35 * width)),
            angle=0.0,
            startAngle=-45,
            endAngle=235,
            color=color,
            thickness=2,
            lineType=cv2.LINE_4
        )

        rectangle_width = 40
        rectangle_height = 20
        x1_rect = x_center - rectangle_width // 2
        x2_rect = x_center + rectangle_width // 2
        y1_rect = (y2 - rectangle_height // 2) + 15
        y2_rect = (y2 + rectangle_height // 2) + 15

        if track_id is not None:
            cv2.rectangle(frame,
                          (int(x1_rect), int(y1_rect)),
                          (int(x2_rect), int(y2_rect)),
                          color,
                          cv2.FILLED)

            x1_text = x1_rect + 12
            if track_id > 99:
                x1_text -= 10

            cv2.putText(
                frame,
                f"{track_id}",
                (int(x1_text), int(y1_rect + 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )

        return frame

    def draw_traingle(self, frame, bbox, color):
        y = int(bbox[1])
        x, _ = get_center_of_bbox(bbox)

        triangle_points = np.array([
            [x, y],
            [x - 10, y - 20],
            [x + 10, y - 20],
        ])
        cv2.drawContours(frame, [triangle_points], 0, color, cv2.FILLED)
        cv2.drawContours(frame, [triangle_points], 0, (0, 0, 0), 2)

        return frame

    def draw_annotations(self, video_frames, tracks):
        output_video_frames = []
        print("Drawing annotations...")
        for frame_num, frame in enumerate(video_frames):
            print(f"Annotating frame {frame_num + 1} / {len(video_frames)}", end='\r')
            frame = frame.copy()

            player_dict = tracks["players"][frame_num]
            ball_dict = tracks["ball"][frame_num]
            referee_dict = tracks["referees"][frame_num]

            # Draw Players
            for track_id, player in player_dict.items():
                frame = self.draw_ellipse(frame, player["bbox"], (0,0,255), track_id)

            # Draw Referee
            for track_id, referee in referee_dict.items():
                 frame = self.draw_ellipse(frame, referee["bbox"], (0, 255, 255), track_id)

            # Draw ball
            for track_id, ball in ball_dict.items():
                ball_bbox = ball["bbox"]
                # Add a check to ensure ball_bbox is not empty or None
                if ball_bbox:
                    frame = self.draw_traingle(frame, ball_bbox, (0, 255, 0))


            output_video_frames.append(frame)
        print("\nAnnotation complete.")

        return output_video_frames