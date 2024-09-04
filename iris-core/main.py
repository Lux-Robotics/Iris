import argparse
import sys
import os
import threading
import time

# Add parent directory to path for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pyapriltags

import detectors.apriltag_detector
import detectors.aruco_detector

import output.foxglove_logger as out
import output.foxglove_server
import output.http_stream
from util.filter_tags import filter_tags
from util.nt_interface import NTInterface
from util.nt_listener import NTListener
from util.pose_estimator import *
from util.state import settings, logger, exec_dir

parser = argparse.ArgumentParser("peninsula_perception")
parser.add_argument(
    "--mode", help="Toggle for operation modes", type=int, default=0, required=False
)
args = parser.parse_args()

# Start logging thread

if args.mode == 2:
    settings.logging.enabled = False
    settings.http_stream.enabled = False
    settings.foxglove_server.enabled = False
    settings.use_networktables = False

logging_thread = threading.Thread(target=out.start)
if settings.logging.enabled:
    logging_thread.daemon = True
    logging_thread.start()

# make sure logging thread has started
time.sleep(0.2)


# Initialize video capture
def init_camera():
    if args.mode == 0:
        if settings.capture == "opencv":
            camera = cv2.VideoCapture(0)
            # camera.set(cv2.CAP_PROP_FRAME_WIDTH, resx)
            # camera.set(cv2.CAP_PROP_FRAME_HEIGHT, state.resy)
        elif settings.capture == "gstreamer":
            camera = cv2.VideoCapture(state.gstreamer_pipeline, cv2.CAP_GSTREAMER)
        else:
            # Mode parameter not valid
            logger.error("Program mode invalid")
            sys.exit()
    elif args.mode == 1:
        camera = cv2.VideoCapture(os.path.join(exec_dir, settings.test_video))
    elif args.mode == 2:
        camera = cv2.VideoCapture(os.path.join(exec_dir, settings.test_video))
    else:
        # Mode parameter not valid
        logger.error("Program mode invalid")
        sys.exit()

    return camera


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

foxglove_server_thread = threading.Thread(target=output.foxglove_server.start)
if settings.foxglove_server.enabled:
    foxglove_server_thread.daemon = True
    foxglove_server_thread.start()

if settings.http_stream.enabled:
    output.http_stream.start()

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

    # Solve for pose
    try:
        if settings.solvepnp_method == "singletag" or len(filtered_detections) <= 1:
            poses = solvepnp_singletag(filtered_detections)
        elif settings.solvepnp_method == "multitag":
            poses = solvepnp_multitag(filtered_detections)
        elif settings.solvepnp_method == "ransac":
            poses = solvepnp_ransac(filtered_detections)
        elif settings.solvepnp_method == "ransac_fallback":
            poses = solvepnp_ransac(filtered_detections)
            if poses == ():
                poses = solvepnp_multitag(filtered_detections)
        else:
            logger.error("Pose estimation mode invalid")
            sys.exit(-1)

    except AssertionError:
        logger.warning("SolvePNP failed with assertion error")
    except Exception as e:
        logger.warning("SolvePNP failed: " + str(e))

    if nt_instance is not None:
        try:
            nt_instance.publish_data(
                poses[0] if len(poses) > 0 else None,
                poses[1] if len(poses) > 1 else None,
                detections,
                new_frame_time,
            )
        except Exception:
            logger.warning("Failed to publish nt4 data")

    nt_listener.update_data(new_frame_time)

    if state.detector_update_needed:
        if settings.detector == "apriltag":
            state.apriltag3_detector = pyapriltags.Detector(
                families=settings.apriltag3.families,
                nthreads=settings.apriltag3.threads,
                quad_decimate=settings.apriltag3.quad_decimate,
                quad_sigma=settings.apriltag3.quad_sigma,
                refine_edges=settings.apriltag3.refine_edges,
            )
            logger.info("Detector updated: " + str(state.apriltag3_detector.params))

        elif settings.detector == "aruco":  # Aruco
            state.aruco_detection_params.aprilTagQuadDecimate = (
                settings.apriltag3.quad_decimate
            )
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

    if not settings.logging.enabled and not settings.foxglove_server.enabled:
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
