import cv2
import time
from util.pose_estimator import solvepnp_singletag
import util.config as config
import argparse
import threading
import display.web_server
from util.output_publisher import NTPublisher

parser = argparse.ArgumentParser("peninsula_perception")
parser.add_argument("--mode", help="Toggle for operation modes", type=int, default=0, required=False)
args = parser.parse_args()


my_thread = threading.Thread(target=display.web_server.start)


match config.settings["detector"]:
    case "aruco":
        from detectors.aruco_detector import find_corners
    case "apriltag3":
        from detectors.apriltag_detector import find_corners

match args.mode:
    case 0:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.resx)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.resy)
    case 1:
        camera = cv2.VideoCapture(config.test_video)
    case 2:
        camera = cv2.VideoCapture(config.test_video)
        config.preview = False

nt_instance = NTPublisher("127.0.0.1")

prev_frame_time = 0

if config.preview:
    my_thread.start()

while True:
    new_frame_time = time.time()
    ret, frame = camera.read()

    if frame is None:
        if args.mode != 0:
            print("Average FPS: " + str(1 / ((config.fps[-1] - config.fps[11]) / len(config.fps[10:]))))
            break
        print("video input not detected")
        time.sleep(0.02)
        continue

    detections = find_corners(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

    # Solve for pose
    poses = solvepnp_singletag(detections)

    nt_instance.publish_data(poses[3] if len(poses) > 0 else None, new_frame_time)

    config.last_frame, config.detections = frame, detections

    if not config.preview and args.mode == 1:
        print("FPS:", 10 / (new_frame_time - config.fps[-10]))

    config.fps.append(new_frame_time)

camera.release()
cv2.destroyAllWindows()
