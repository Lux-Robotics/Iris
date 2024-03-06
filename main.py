import argparse
import sys
import threading
import time
import output.foxglove_logger as out

import cv2

import output.foxglove_server
import util.config as config
from util.nt_interface import NTInterface
from util.pose_estimator import (
    solvepnp_singletag,
    solvepnp_multitag,
    solvepnp_ransac,
    multitag_ap3p,
)
from util.filter_tags import filter_tags

parser = argparse.ArgumentParser("peninsula_perception")
parser.add_argument(
    "--mode", help="Toggle for operation modes", type=int, default=0, required=False
)
args = parser.parse_args()

# Start logging thread

logging_thread = threading.Thread(target=out.start)
if config.logger_enabled:
    logging_thread.daemon = True
    logging_thread.start()

# make sure logging thread has started
time.sleep(0.2)

# Import apriltag detector
try:
    module = __import__(
        "detectors." + config.settings["detector"] + "_detector", fromlist=[""]
    )
    find_corners = getattr(module, "find_corners")
except ImportError:
    config.logger.error("The specified detector does not exist")
    sys.exit()


# Initialize video capture
def init_camera():
    if args.mode == 0:
        if config.capture_mode == "opencv":
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.resx)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.resy)
        elif config.capture_mode == "gstreamer":
            camera = cv2.VideoCapture(config.gstreamer_pipeline, cv2.CAP_GSTREAMER)
        else:
            # Mode parameter not valid
            config.logger.error("Program mode invalid")
            sys.exit()
    elif args.mode == 1:
        camera = cv2.VideoCapture(config.test_video)
    elif args.mode == 2:
        camera = cv2.VideoCapture(config.test_video)
        config.logger_enabled = False
        config.use_nt = False
    else:
        # Mode parameter not valid
        config.logger.error("Program mode invalid")
        sys.exit()

    return camera


try:
    camera = init_camera()
except Exception:
    config.logger.error("Failed to initialize video capture")
    sys.exit()

nt_instance = None

if config.use_nt:
    nt_instance = NTInterface(config.server_ip)

prev_frame_time = 0

if config.stream_enabled:
    server_thread = threading.Thread(target=output.foxglove_server.start)
    server_thread.daemon = True
    server_thread.start()

while True:
    # read data from networktables
    nt_instance.get_states()

    ret, frame = camera.read()
    new_frame_time = time.time()

    # Latency compensation estimate
    new_frame_time -= (1 / config.camera_fps) / 2

    # Bad camera return value
    if not ret:
        if args.mode == 0:
            config.logger.warning("video input not detected")

            # Attempt to reinitialize camera after 0.1 seconds
            config.bad_frames += 1
            if config.bad_frames > 10:
                break

            time.sleep(0.1)
            camera = init_camera()
            continue

        else:
            info = config.logger.info(
                "Average FPS: "
                + str(1 / ((config.fps[-1] - config.fps[11]) / len(config.fps[10:])))
            )
            break

    if config.detector == "aruco":
        detections = find_corners(frame)
    else:
        detections = find_corners(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

    filtered_detections, ignored_detections = filter_tags(detections)

    poses = tuple()

    # Solve for pose
    try:
        if config.pose_estimation_mode == "singletag" or len(filtered_detections) <= 1:
            poses = solvepnp_singletag(filtered_detections)
        elif config.pose_estimation_mode == "multitag":
            poses = solvepnp_multitag(filtered_detections)
        elif config.pose_estimation_mode == "ransac":
            poses = solvepnp_ransac(filtered_detections)
        elif config.pose_estimation_mode == "ransac_fallback":
            poses = solvepnp_ransac(filtered_detections)
            if poses == ():
                poses = solvepnp_multitag(filtered_detections)
        elif config.pose_estimation_mode == "multitag_ap3p":
            poses = multitag_ap3p(filtered_detections)
        else:
            config.logger.error("Pose estimation mode invalid")
            sys.exit(-1)
    except AssertionError:
        config.logger.warning("SolvePNP failed with assertion error")
    except Exception as e:
        config.logger.warning("SolvePNP failed: " + str(e))

    if nt_instance is not None:
        try:
            nt_instance.publish_data(
                poses[0] if len(poses) > 0 else None,
                poses[1] if len(poses) > 1 else None,
                detections,
                new_frame_time,
            )
        except Exception:
            config.logger.warning("Failed to publish nt4 data")

    (
        config.last_frame,
        config.filtered_detections,
        config.ignored_detections,
        config.poses,
    ) = (frame, filtered_detections, ignored_detections, poses)
    config.new_data = True

    if not config.logger_enabled and args.mode == 1:
        print("FPS:", 10 / (new_frame_time - config.fps[-10]))

    config.fps.append(new_frame_time)

    if config.logger_enabled and not logging_thread.is_alive():
        config.logger.error("Logging thread unalived")
        config.logger_enabled = (
            False  # Do not exit since logging does not affect primary function
        )

camera.release()

sys.exit()
