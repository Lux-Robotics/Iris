import argparse
import os
import sys
import threading
import time

# Add parent directory to path for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2

import detectors.apriltag_detector
import detectors.aruco_detector
import output.foxglove_logger
import output.foxglove_server
import output.http_stream
import output.web_server
import util.pose_estimator
import util.state as state
from util.filter_tags import filter_tags
from util.nt_interface import NTInterface, NTListener
from util.state import Platform, exec_dir, logger, settings

parser = argparse.ArgumentParser("iris")
parser.add_argument(
    "--mode", help="Toggle for operation modes", type=int, default=0, required=False
)
parser.add_argument(
    "--video", help="Video path", type=str, default=None, required=False
)
args = parser.parse_args()

# Start logging thread

if args.video is not None:
    args.mode = 1
if args.mode == 2:
    settings.logging.enabled = False
    settings.http_stream.enabled = False
    settings.foxglove_server.enabled = False
    settings.use_networktables = False

logging_thread = threading.Thread(target=output.foxglove_logger.start)
if settings.logging.enabled:
    logging_thread.daemon = True
    logging_thread.start()

# make sure logging thread has started
time.sleep(0.2)


# Initialize video capture
def init_camera():
    if args.mode == 0:
        if state.platform == Platform.IRIS:
            if settings.capture == "gstreamer":
                cap = cv2.VideoCapture(0)
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc("M", "J", "P", "G"))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
                cap.set(cv2.CAP_PROP_FPS, 50)
                return cap
            return cv2.VideoCapture(11)
        elif state.platform == Platform.DEV:
            return cv2.VideoCapture(0)
            # camera.set(cv2.CAP_PROP_FRAME_WIDTH, resx)
            # camera.set(cv2.CAP_PROP_FRAME_HEIGHT, state.resy)
        else:
            # Mode parameter not valid
            logger.error("Program mode invalid")
            sys.exit()
    elif args.video is not None:
        return cv2.VideoCapture(args.video)
    elif args.mode == 1:
        return cv2.VideoCapture(os.path.join(exec_dir, settings.test_video))
    elif args.mode == 2:
        return cv2.VideoCapture(os.path.join(exec_dir, settings.test_video))
    else:
        # Mode parameter not valid
        logger.error("Program mode invalid")
        sys.exit()


try:
    camera = init_camera()
except Exception as e:
    logger.error("Failed to initialize video capture: " + str(e))
    sys.exit()

nt_instance = None

if settings.use_networktables:
    nt_instance = NTInterface(state.get_server_ip())

nt_listener = NTListener()

prev_frame_time = 0

foxglove_server_thread = threading.Thread(
    target=output.foxglove_server.start, daemon=True
)
if settings.foxglove_server.enabled:
    foxglove_server_thread.start()

web_server_thread = threading.Thread(target=output.web_server.start, daemon=True)
if settings.http_stream.enabled:
    output.http_stream.start()
    web_server_thread.start()

while True:
    # read data from networktables
    if settings.use_networktables:
        nt_instance.get_states()

    ret, frame = camera.read()
    new_frame_time = time.time()

    state.frame_times.append(new_frame_time)
    # FPS Calculation
    if len(state.frame_times) >= 10:
        state.fps = 9 / (state.frame_times[-1] - state.frame_times[-10])
    elif len(state.frame_times) > 1:
        state.fps = (len(state.frame_times) - 1) / (
            state.frame_times[-1] - state.frame_times[0]
        )
    else:
        state.fps = 0

    # Latency compensation estimate
    new_frame_time -= (1 / settings.camera.fps) / 2

    # Bad camera return value
    if not ret:
        if args.mode == 0:
            logger.warning("video input not detected")

            # Attempt to reinitialize camera after 0.1 seconds
            state.bad_frames += 1
            if state.bad_frames > 10:
                break

            time.sleep(0.1)
            camera = init_camera()
            continue

        elif args.mode == 1:
            camera = init_camera()
            continue

        else:
            info = logger.info("Average FPS: " + str(state.fps))
            break

    if settings.detector == "aruco":
        detections = detectors.aruco_detector.find_corners(frame)
    elif settings.detector == "apriltag":
        detections = detectors.apriltag_detector.find_corners(
            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        )
    else:
        detections = []

    filtered_detections, ignored_detections = filter_tags(detections)

    poses = tuple()
    targets = []

    # Solve for pose
    try:
        if settings.solvepnp_method == "singletag" or len(filtered_detections) <= 1:
            poses = util.pose_estimator.solvepnp_singletag(filtered_detections)
        elif settings.solvepnp_method == "multitag":
            poses = util.pose_estimator.solvepnp_multitag(filtered_detections)
        elif settings.solvepnp_method == "ransac":
            poses = util.pose_estimator.solvepnp_ransac(filtered_detections)
        elif settings.solvepnp_method == "ransac_fallback":
            poses = util.pose_estimator.solvepnp_ransac(filtered_detections)
            if poses == ():
                poses = util.pose_estimator.solvepnp_multitag(filtered_detections)
        else:
            logger.error("Pose estimation mode invalid")
            sys.exit(-1)

        for detection in detections:
            targets.append(util.pose_estimator.get_tag_angle_offset(detection))

    except AssertionError:
        logger.warning("SolvePNP failed with assertion error")
    except Exception as e:
        logger.warning("SolvePNP failed: " + str(e))

    if nt_instance is not None:
        try:
            nt_instance.publish_data(
                poses[0] if len(poses) > 0 else None,
                poses[1] if len(poses) > 1 else None,
                targets,
                detections,
                new_frame_time,
            )
        except Exception as e:
            logger.warning("Failed to publish nt4 data" + str(e))

    nt_listener.update_data(new_frame_time)

    if state.detector_update_needed:
        if settings.detector == "apriltag":
            state.apriltag3_detector = state.get_apriltag3_detector()
            logger.info("Detector updated: " + str(state.apriltag3_detector.params))

        elif settings.detector == "aruco":  # Aruco
            state.aruco_detection_params = state.get_aruco_detection_params()
            state.aruco_dict = state.get_aruco_dict_from_string()
            logger.info("Detector updated: " + str(state.aruco_detection_params))

        state.detector_update_needed = False

    (
        state.last_frame,
        state.filtered_detections,
        state.ignored_detections,
        state.poses,
        state.last_frame_time,
    ) = (frame, filtered_detections, ignored_detections, poses, new_frame_time)
    state.new_data = True

    if args.mode == 2:
        logger.info("FPS:" + str(state.fps))

    if settings.http_stream.enabled:
        output.http_stream.get_frame()

    if settings.logging.enabled and not logging_thread.is_alive():
        logger.error("Logging thread unalived")
        settings.logging.enabled = (
            False  # Do not exit since logging does not affect primary function
        )

camera.release()

sys.exit()
