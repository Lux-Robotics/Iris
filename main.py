import cv2
import time
from util.pose_estimator import solvepnp_singletag
import util.config as constants
import argparse
import threading
import display.web_server

parser = argparse.ArgumentParser("peninsula_perception")
parser.add_argument("--mode", help="Toggle for operation modes", type=int, default=0, required=False)
args = parser.parse_args()


my_thread = threading.Thread(target=display.web_server.start)


match constants.settings["detector"]:
    case "aruco":
        from detectors.aruco_detector import find_corners
    case "apriltag3":
        from detectors.apriltag_detector import find_corners

match args.mode:
    case 0:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, constants.resx)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, constants.resy)
    case 1:
        camera = cv2.VideoCapture(constants.test_video)
    case 2:
        camera = cv2.VideoCapture(constants.test_video)
        constants.preview = False


prev_frame_time = 0

if constants.preview:
    my_thread.start()

while True:
    new_frame_time = time.time()
    ret, frame = camera.read()

    if frame is None:
        if args.mode == 2:
            print("Average FPS: " + str(1/((constants.fps[-1]-constants.fps[11])/len(constants.fps[10:]))))
            break
        print("video input not detected")
        time.sleep(0.02)
        continue

    detections = find_corners(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

    # Solve for pose
    constants.poses = solvepnp_singletag(detections)

    constants.last_frame, constants.detections = frame, detections

    if not constants.preview:
        print("FPS:", 10 / (new_frame_time - constants.fps[-10]))

    constants.fps.append(new_frame_time)

camera.release()
cv2.destroyAllWindows()
