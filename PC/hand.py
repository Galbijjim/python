import sys
import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    cv2.imshow('Camera', frame)

    key = chr(cv2.waitKey(1) & 0xFF)
    if key == 'q':
        cap.release()
        cv2.destoryAllWindows()
        break