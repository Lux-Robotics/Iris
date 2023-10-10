import cv2
import time
from util.pose_estimator import solvepnp_singletag, solvepnp_multitag, solvepnp_apriltag
import util.config as config
import argparse
import threading
from util.output_publisher import NTPublisher
import sys

parser = argparse.ArgumentParser("peninsula_perception")
parser.add_argument("--mode", help="Toggle for operation modes", type=int, default=0, required=False)
args = parser.parse_args()

match config.settings["detector"]:
    case "aruco":
        from detectors.aruco_detector import find_corners
    case "apriltag3":
        from detectors.apriltag_detector import find_corners

match args.mode:
    case 0:
        match config.capture_mode:
            case "opencv":
                camera = cv2.VideoCapture(0)
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.resx)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.resy)
            case "gstreamer":
                camera = cv2.VideoCapture("v4l2src device=/dev/video0 extra_controls=\"c,exposure_time_absolute=" + str(
                    config.camera_exposure_time) + ",brightness=" + str(
                    config.camera_brightness) + "\" ! video/x-raw framerate=" + str(
                    config.camera_fps) + "/1 ! appsink drop=1",
                                          cv2.CAP_GSTREAMER)
    case 1:
        camera = cv2.VideoCapture(config.test_video)
    case 2:
        camera = cv2.VideoCapture(config.test_video)
        config.preview = False
        config.use_nt = False

if config.use_nt:
    nt_instance = NTPublisher("127.0.0.1")

prev_frame_time = 0

# Start web stream thread
if config.preview:
    import display.rerun_server

    display_thread = threading.Thread(target=display.rerun_server.start)
    display_thread.daemon = True
    display_thread.start()

while True:
    ret, frame = camera.read()
    new_frame_time = time.time()

    # Latency compensation estimate
    new_frame_time -= (1 / config.camera_fps) / 2

    if frame is None:
        if args.mode != 0:
            print("Average FPS: " + str(1 / ((config.fps[-1] - config.fps[11]) / len(config.fps[10:]))))
            break
        print("video input not detected")
        time.sleep(0.02)
        continue

    detections = find_corners(frame)

    # Solve for pose
    if config.pose_estimation_mode == "singletag":
        poses = solvepnp_singletag(detections)
    elif config.pose_estimation_mode == "multitag":
        poses = solvepnp_multitag(detections)

    if config.use_nt:
        nt_instance.publish_data(poses[0] if len(poses) > 0 else None, poses[1] if len(poses) > 1 else None,
                                 len(detections),
                                 new_frame_time)

    config.last_frame, config.detections, config.poses = frame, detections, poses
    config.new_data = True

    if not config.preview and args.mode == 1:
        print("FPS:", 10 / (new_frame_time - config.fps[-10]))

    config.fps.append(new_frame_time)

camera.release()

sys.exit()
