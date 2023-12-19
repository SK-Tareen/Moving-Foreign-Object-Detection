import cv2
import imutils
import datetime
import numpy as np

cap = cv2.VideoCapture(0)
avg = None
idx = 0
motionCounter = 0
minCounter = 20

cv2.namedWindow('Object_Detector', cv2.WINDOW_NORMAL)


while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_LINEAR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if avg is None:
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        continue

    cv2.accumulateWeighted(gray, avg, 0.7)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

    thresh = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:
        if cv2.contourArea(c) < 10000:
            continue

        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Foreign Object Detected"

        cv2.putText(frame, text, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        motionCounter += 1
        if motionCounter >= minCounter:
            idx += 1
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'C:/Users/hp/Desktop/FOD internship/time stamp/{timestamp}_{idx}.jpg'
            cv2.imwrite(filename, frame)
            motionCounter = 0

    if prev_gray is not None:
        # Calculate optical flow
        pts, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_pts, None, **lk_params)

        if pts is not None and prev_pts is not None:
            speeds = []  # List to store speeds of keypoints
            directions = []  # List to store direction coordinates

            for i, (new, old) in enumerate(zip(pts, prev_pts)):
                a, b = new.ravel().astype(int)
                c, d = old.ravel().astype(int)
                
               
                # Draw an arrow to show the optical flow direction
                mask = cv2.arrowedLine(frame, (a, b), (c, d), (0, 0, 255), 2)

            # Calculate average speed
            if len(speeds) > 0:
                average_speed = np.mean(speeds)
                cv2.putText(frame, f"Avg Speed: {average_speed:.2f} px/frame", (20, frame.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            

    cv2.imshow("Object_Detector", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    prev_gray = gray.copy()
    prev_pts = cv2.goodFeaturesToTrack(prev_gray, mask=None, maxCorners=100, qualityLevel=0.3,
                                       minDistance=7, blockSize=7)

cap.release()
cv2.destroyAllWindows()
