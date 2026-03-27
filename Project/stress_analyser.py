import cv2
import mediapipe as mp
import numpy as np
import math
import time

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

cap = cv2.VideoCapture(0)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

def eye_aspect_ratio(landmarks, eye_indices, w, h):
    points = []
    for idx in eye_indices:
        x = int(landmarks[idx].x * w)
        y = int(landmarks[idx].y * h)
        points.append((x, y))

    A = math.dist(points[1], points[5])
    B = math.dist(points[2], points[4])
    C = math.dist(points[0], points[3])

    ear = (A + B) / (2.0 * C)
    return ear

blink_counter = 0
closed_frames = 0
head_positions = []

start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    stress_score = 0

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:

            # --- Blink Detection ---
            ear_left = eye_aspect_ratio(face_landmarks.landmark, LEFT_EYE, w, h)
            ear_right = eye_aspect_ratio(face_landmarks.landmark, RIGHT_EYE, w, h)
            ear = (ear_left + ear_right) / 2

            if ear < 0.20:
                closed_frames += 1
            else:
                if closed_frames > 3:
                    blink_counter += 1
                closed_frames = 0

            # --- Head Movement Tracking ---
            nose = face_landmarks.landmark[1]
            nose_x = int(nose.x * w)
            nose_y = int(nose.y * h)

            head_positions.append((nose_x, nose_y))
            if len(head_positions) > 20:
                head_positions.pop(0)

            if len(head_positions) > 10:
                variance = np.var(head_positions)
                stress_score += variance / 1000

            # --- Blink contribution ---
            stress_score += blink_counter * 0.5

            # --- Display ---
            cv2.putText(frame, f"Blinks: {blink_counter}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(frame, f"Stress Score: {round(stress_score,2)}",
                        (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255) if stress_score > 5 else (0, 255, 0),
                        2)

            if stress_score > 5:
                cv2.putText(frame, "High Stress Detected",
                            (30, 120),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 3)

    cv2.imshow("Micro Expression Stress Analyzer", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()