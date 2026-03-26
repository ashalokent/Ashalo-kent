from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import numpy as np
import random  # placeholder for demo emotions

app = Flask(__name__)

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Load emojis
emoji_dict = {
    "happy": cv2.imread("emojis/happy.png", cv2.IMREAD_UNCHANGED),
    "sad": cv2.imread("emojis/sad.png", cv2.IMREAD_UNCHANGED),
    "angry": cv2.imread("emojis/angry.png", cv2.IMREAD_UNCHANGED),
}

# ---- Use Phone Camera as IP Webcam ----
# Replace with your phone's IP Webcam URL (check IP Webcam app)
cap = cv2.VideoCapture("http://192.168.137.78:8080/video")  # Example IP, replace it

def detect_emotion(face_landmarks):
    """
    Simple placeholder for emotion detection.
    Replace this with a real model for accurate results.
    """
    if face_landmarks:
        return random.choice(["happy", "sad", "angry"])
    return None

def overlay_emoji(frame, emoji_img):
    """
    Overlay PNG emoji with transparency on the frame
    """
    emoji_img = cv2.resize(emoji_img, (100, 100))
    y_offset, x_offset = 50, 50
    y1, y2 = y_offset, y_offset + emoji_img.shape[0]
    x1, x2 = x_offset, x_offset + emoji_img.shape[1]

    # Split channels for alpha blending
    alpha_s = emoji_img[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s

    for c in range(0, 3):
        frame[y1:y2, x1:x2, c] = (alpha_s * emoji_img[:, :, c] +
                                  alpha_l * frame[y1:y2, x1:x2, c])
    return frame

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)

        emotion = None
        if results.multi_face_landmarks:
            emotion = detect_emotion(results.multi_face_landmarks[0])

        if emotion and emotion in emoji_dict:
            frame = overlay_emoji(frame, emoji_dict[emotion])

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)