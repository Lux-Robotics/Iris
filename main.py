import cv2
import time
from detectors.aruco_detector import draw_detections
from util.pose_estimator import solvepnp_singletag
import util.constants as constants

match constants.settings["detector"]:
    case "aruco":
        from detectors.aruco_detector import find_corners
    case "apriltag3":
        from detectors.apriltag_detector import find_corners

camera = cv2.VideoCapture("testdata/output.avi")
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)

prev_frame_time = 0
fps = [0 for x in range(10)]

while True:
    new_frame_time = time.time()
    ret, frame = camera.read()

    if frame is None:
        print("video input not detected")
        time.sleep(0.02)
        continue

    detections = find_corners(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

    # Solve for pose
    poses = solvepnp_singletag(detections)

    if constants.preview:
        im = draw_detections(frame, detections)

        if constants.preview_fps:
            cv2.putText(im, "FPS: " + str(10 / (new_frame_time - fps[-10])), (7, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (100, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(im, "Frame: " + str(len(fps) - 9), (7, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 2,
                        cv2.LINE_AA)

        if constants.preview_pose:
            try:
                pose_text = " y: " + str(poses[3][1][0][0].round(2)) + " z: " + str(
                    poses[3][1][1][0].round(2)) + " x: " + str(poses[3][1][2][0].round(2))
                cv2.putText(im, pose_text, (7, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 2, cv2.LINE_AA)
            except:
                pass
        cv2.imshow("image", im)

        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break
        if constants.preview_frame:
            cv2.waitKey(0)

    else:
        print("FPS:", 10 / (new_frame_time - fps[-10]))

    fps.append(new_frame_time)

camera.release()
cv2.destroyAllWindows()
