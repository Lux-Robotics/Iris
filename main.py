import argparse
import sys
import threading
import time

import output.foxglove_logger as out
import output.foxglove_server
import output.http_stream
from util.config import settings, logger
from util.filter_tags import filter_tags
from util.nt_interface import NTInterface
from util.pose_estimator import *

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

# Import apriltag detector
try:
    module = __import__("detectors." + settings.detector + "_detector", fromlist=[""])
    find_corners = getattr(module, "find_corners")
except ImportError:
    logger.error("The specified detector does not exist")
    sys.exit()


# Initialize video capture
def init_camera():
    if args.mode == 0:
        if settings.capture == "opencv":
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, resx)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.resy)
        elif settings.capture == "gstreamer":
            camera = cv2.VideoCapture(config.gstreamer_pipeline, cv2.CAP_GSTREAMER)
        else:
            # Mode parameter not valid
            logger.error("Program mode invalid")
            sys.exit()
    elif args.mode == 1:
        camera = cv2.VideoCapture(settings.test_video)
    elif args.mode == 2:
        camera = cv2.VideoCapture(settings.test_video)
    else:
        # Mode parameter not valid
        logger.error("Program mode invalid")
        sys.exit()

    return camera


try:
    camera = init_camera()
except Exception:
    logger.error("Failed to initialize video capture")
    sys.exit()

nt_instance = None

if settings.use_networktables:
    nt_instance = NTInterface(settings.server_ip)

prev_frame_time = 0

foxglove_server_thread = threading.Thread(target=output.foxglove_server.start)
if settings.foxglove_server.enabled:
    foxglove_server_thread.daemon = True
    foxglove_server_thread.start()

http_stream_thread = threading.Thread(target=output.http_stream.start)
if settings.http_stream.enabled:
    http_stream_thread.daemon = True
    http_stream_thread.start()

while True:
    # read data from networktables
    if settings.use_networktables:
        nt_instance.get_states()

    ret, frame = camera.read()
    new_frame_time = time.time()

    # Latency compensation estimate
    new_frame_time -= (1 / settings.camera.fps) / 2

    # Bad camera return value
    if not ret:
        if args.mode == 0:
            logger.warning("video input not detected")

            # Attempt to reinitialize camera after 0.1 seconds
            config.bad_frames += 1
            if config.bad_frames > 10:
                break

            time.sleep(0.1)
            camera = init_camera()
            continue

        elif args.mode == 1:
            camera = init_camera()
            continue

        else:
            info = logger.info(
                "Average FPS: "
                + str(1 / ((config.fps[-1] - config.fps[11]) / len(config.fps[10:])))
            )
            break

    if settings.detector == "aruco":
        detections = find_corners(frame)
    else:
        detections = find_corners(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

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

    (
        config.last_frame,
        config.filtered_detections,
        config.ignored_detections,
        config.poses,
        config.last_frame_time,
    ) = (frame, filtered_detections, ignored_detections, poses, new_frame_time)
    config.new_data = True

    if not settings.logging.enabled and not settings.foxglove_server.enabled:
        logger.info("FPS:" + str(10 / (new_frame_time - config.fps[-10])))

    config.fps.append(new_frame_time)

    if settings.logging.enabled and not logging_thread.is_alive():
        logger.error("Logging thread unalived")
        settings.logging.enabled = (
            False  # Do not exit since logging does not affect primary function
        )

camera.release()

sys.exit()
