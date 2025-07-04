import cv2

def read_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

def save_video(output_video_frames, output_path, fps=25):
    if not output_video_frames:
        print("No frames to save.")
        return

    height, width, _ = output_video_frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec for .mp4
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame in output_video_frames:
        out.write(frame)

    out.release()
    print(f"Video saved successfully to {output_path}")