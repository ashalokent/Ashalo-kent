import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)

# Give camera time to adjust
time.sleep(2)

# Capture background
for i in range(30):
    ret, background = cap.read()
background = np.flip(background, axis=1)

print("Background captured!")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    frame = np.flip(frame, axis=1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Red color range
    lower_red1 = np.array([0,120,70])
    upper_red1 = np.array([10,255,255])
    
    lower_red2 = np.array([170,120,70])
    upper_red2 = np.array([180,255,255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 + mask2

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
    mask = cv2.dilate(mask, np.ones((3,3),np.uint8), iterations=1)

    mask_inv = cv2.bitwise_not(mask)

    res1 = cv2.bitwise_and(background, background, mask=mask)
    res2 = cv2.bitwise_and(frame, frame, mask=mask_inv)

    final_output = cv2.addWeighted(res1, 1, res2, 1, 0)

    cv2.imshow("Invisible Cloak", final_output)

    if cv2.waitKey(1) == 27:  # Press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()