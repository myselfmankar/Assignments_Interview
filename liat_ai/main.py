from utils import read_video, save_video
from tracker import Tracker
import os

# This script initializes a video tracker using a custom model and processes a video file to track objects.
base_path = os.path.dirname(os.path.abspath(__file__))
CUSTOM_MODEL_PATH = "your_model_path.pt"  # Replace with your actual model path
VIDEO_PATH = "input_video/15sec_input_720p.mp4"  # Replace with your actual video path
OUTPUT_PATH = "output_video/tracked_output.mp4"  # Path to save the output video
TRACKER_CONFIG = "custom_botsort.yaml"

def main():
    # Optionally specify a stub_path to save/load tracking results
    stub_path = os.path.join(base_path, 'tracker_stubs', 'player_reid_tracks.pkl')

    tracker = Tracker(model_path=CUSTOM_MODEL_PATH)
    tracks = tracker.get_object_tracks(
        video_path=VIDEO_PATH, 
        tracker_config=TRACKER_CONFIG, 
        read_from_stub=False, 
        stub_path=stub_path
    )

    video_frames = read_video(VIDEO_PATH)

    output_video_frame = tracker.draw_tracks_on_frames(video_frames, tracks)

    save_video(output_path=OUTPUT_PATH, frames=output_video_frame, fps=30)