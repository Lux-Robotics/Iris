import argparse
import sys
import threading
import time

import cv2

import output.foxglove_server
import util.config as config
from util.output_publisher import NTPublisher
from util.pose_estimator import solvepnp_singletag, solvepnp_multitag

parser = argparse.ArgumentParser("peninsula_perception")
parser.add_argument("--mode", help="Toggle for operation modes", type=int, default=0, required=False)
# parser.add_argument("--log-level", help="Set log level (DEBUG, INFO, WARNING, ERROR)", type=str, default="INFO")
args = parser.parse_args()

# Start logging thread
if config.preview:
    import output.foxglove_logger as out

    display_thread = threading.Thread(target=out.start)
    display_thread.daemon = True
    display_thread.start()

# Import apriltag detector
try:
    module = __import__("detectors." + config.settings["detector"] + "_detector", fromlist=[''])
    find_corners = getattr(module, 'find_corners')
except ImportError:
    config.logger.error("The specified detector does not exist")
    sys.exit()

# Initialize video capture
if args.mode == 0:
    if config.capture_mode == "opencv":
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.resx)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.resy)
    elif config.capture_mode == "gstreamer":
        # Specific for 011
        camera = cv2.VideoCapture(
            "v4l2src device=/dev/video" + str(
                config.camera_id) + " extra_controls=\"c," + config.gstreamer_config + "\" ! image/jpeg,format=MJPG,width=" + str(
                config.resx) + ",height=" + str(config.resy) + " ! jpegdec ! appsink drop=1", cv2.CAP_GSTREAMER)
    else:
        # Mode parameter not valid
        config.logger.error("Program mode invalid")
        sys.exit()
elif args.mode == 1:
    camera = cv2.VideoCapture(config.test_video)
elif args.mode == 2:
    camera = cv2.VideoCapture(config.test_video)
    config.preview = False
    config.use_nt = False
else:
    # Mode parameter not valid
    config.logger.error("Program mode invalid")
    sys.exit()

nt_instance = None

if config.use_nt:
    nt_instance = NTPublisher(config.server_ip)

prev_frame_time = 0

server_thread = threading.Thread(target=output.foxglove_server.start)
server_thread.daemon = True
server_thread.start()

while True:
    ret, frame = camera.read()
    new_frame_time = time.time()

    # Latency compensation estimate
    new_frame_time -= (1 / config.camera_fps) / 2

    if frame is None:
        if args.mode != 0:
            info = config.logger.info(
                "Average FPS: " + str(1 / ((config.fps[-1] - config.fps[11]) / len(config.fps[10:]))))
            break
        config.logger.warning("video input not detected")
        time.sleep(0.02)
        continue

    detections = find_corners(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

    # Solve for pose
    if config.pose_estimation_mode == "singletag":
        poses = solvepnp_singletag(detections)
    elif config.pose_estimation_mode == "multitag":
        poses = solvepnp_multitag(detections)
    else:
        config.logger.error("Pose estimation mode invalid")
        sys.exit(-1)  # TODO: make proper error

    if nt_instance is not None:
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
