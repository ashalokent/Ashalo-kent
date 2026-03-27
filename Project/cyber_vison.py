import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)
start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize
    frame = cv2.resize(frame, (800, 600))

    # Convert to gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Edge detection
    edges = cv2.Canny(gray, 50, 150)

    # Convert edges to BGR
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    # Neon blue glow
    neon = np.zeros_like(frame)
    neon[:, :, 0] = edges * 2  # Blue channel boost

    # Combine original + neon edges
    cyber = cv2.addWeighted(frame, 0.7, neon, 1.2, 0)

    # Add scanning line animation
    scan_y = int((time.time() * 200) % 600)
    cv2.line(cyber, (0, scan_y), (800, scan_y), (255, 0, 0), 2)

    # Add HUD circles
    cv2.circle(cyber, (400, 300), 150, (255, 0, 0), 2)
    cv2.circle(cyber, (400, 300), 200, (255, 0, 0), 1)

    # FPS counter
    fps = int(1 / (time.time() - start_time))
    start_time = time.time()
    cv2.putText(cyber, f"FPS: {fps}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 255), 2)

    cv2.imshow("CYBER VISION", cyber)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()