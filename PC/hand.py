import cv2
from cvzone.HandTrackingModule import HandDetector

cap = None
detect = None

def setup():
    global cap
    cap = cv2.VideoCapture(0)
    detect = HandDetector(maxHands=1, detectionCon=0.8)

def toDo(frame):
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret = detect.findHands(frame)
    print(ret)
    return frame

def loop():
    ret, frame = cap.read()
    frame = toDo(frame)
    cv2.inshow('Camera', frame)

    key = chr(cv2.waitKey(1) & 0xFF).lower()
    if key == 'q':
        cap.release()
        cv2.destroyAllWindows()

def main():
    setup()
    while True:
        loop()

if __name__ == '__main__':
    main()