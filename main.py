import cv2
import time
# import cv2.cv as cv
# from apriltagdetect import find_corners, draw_detections
from detectors.aruco_detector import find_corners, draw_detections
from util.pose_estimator import solvepnp_singletag

camera = cv2.VideoCapture("testdata/output.avi")
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)

prev_frame_time = 0
fps = [0 for x in range(10)]


while True:
    new_frame_time = time.time()
    ret, frame = camera.read()
    # print(frame.shape)
    # image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    image = frame
    ids, corners = find_corners(image)
    im = draw_detections(frame, zip(ids, corners))
    a = solvepnp_singletag(zip(ids, corners))
    # print(a)
    # if 3 in a:
    #     print("y:", a[3][1][0][0].round(2), "z:", a[3][1][1][0].round(2), "x:", a[3][1][2][0].round(2))

    cv2.putText(im, "FPS: " + str(10/(new_frame_time - fps[-10])), (7, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 2, cv2.LINE_AA)
    print(str(10/(new_frame_time - fps[-10])))
    cv2.imshow("image", im)

    k = cv2.waitKey(1) & 0xff
    if k == 27:
        break
    fps.append(new_frame_time)
    fps = fps[-10:]

camera.release()
cv2.destroyAllWindows()
