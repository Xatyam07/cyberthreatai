import cv2
import tempfile
import os
import numpy as np

# Haarcascade face detector (lightweight & fast)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

def extract_frames(video_path, frame_skip=20):
    """
    Extract frames every N frames from video
    """
    cap = cv2.VideoCapture(video_path)
    frames = []
    count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if count % frame_skip == 0:
            frames.append(frame)

        count += 1

    cap.release()
    return frames


def detect_faces(frames):
    """
    Count how many frames contain faces
    """
    face_frames = 0

    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            face_frames += 1

    return face_frames


def analyze_video(file_bytes):
    """
    MAIN VIDEO ANALYSIS FUNCTION
    Returns deepfake risk score
    """

    # Save uploaded video temporarily
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp.write(file_bytes)
    temp.close()

    # Extract frames
    frames = extract_frames(temp.name)

    if len(frames) == 0:
        return 10  # no frames → low risk

    # Face detection analysis
    face_frames = detect_faces(frames)
    face_ratio = face_frames / len(frames)

    # ---- Risk logic ----
    risk = 20

    # If face appears in most frames → talking-head video → deepfake risk higher
    if face_ratio > 0.7:
        risk += 40

    # Very short videos often suspicious
    if len(frames) < 10:
        risk += 20

    # Cleanup temp file
    os.remove(temp.name)

    return min(risk, 95)
