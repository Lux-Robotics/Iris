import json
import os
import logging

import apriltag
import cv2
import numpy as np
from wpimath.geometry import *

from util.vision_types import TagCoordinates

logging.basicConfig(level="INFO", format='%(asctime)s: [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("perception")

v = open("package.json", 'r')
version = json.load(v)["version"]
v.close()

f = open("config.json", 'r')
settings = json.load(f)
f.close()

# Camera config
camera_fps = settings["camera"]["fps"]

gstreamer_pipeline = os.environ.get("GSTREAMER_PIPELINE", settings["camera"]["pipeline"])

calibration_path = os.environ.get("CALIBRATION_FILE", settings["camera"]["calibration"])

c = open(calibration_path, 'r')
calibration = json.load(c)
camera_matrix = np.array(calibration["cameraMatrix"])
dist_coeffs = np.array(calibration["distCoeffs"])
resx, resy = tuple(calibration["resolution"])
c.close()

# networktables
use_nt = settings["use_networktables"]
server_ip = os.environ.get("SERVER_IP", settings["server_ip"])
device_id = os.environ.get("DEVICE_ID", settings["device_id"])

# Setup detection params
detector = settings["detector"]
if detector == "aruco":
    detection_params = cv2.aruco.DetectorParameters()
    detection_params.useAruco3Detection = settings["aruco"]["aruco3"]
    detection_params.aprilTagQuadDecimate = settings["aruco"]["decimate"]

    if settings["aruco"]["corner_refinement"] == "none":
        detection_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_NONE
    elif settings["aruco"]["corner_refinement"] == "subpix":
        detection_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        detection_params.cornerRefinementWinSize = settings["aruco"]["refinement_window"]

elif detector == "apriltag3":
    detector_options = apriltag.DetectorOptions(families='tag16h5')
    detector_options.border = settings["apriltag3"]["border"]
    detector_options.nthreads = settings["apriltag3"]["threads"]
    detector_options.quad_decimate = settings["apriltag3"]["quad_decimate"]
    detector_options.quad_blur = settings["apriltag3"]["quad_blur"]
    detector_options.refine_edges = settings["apriltag3"]["refine_edges"]
    detector_options.refine_decode = settings["apriltag3"]["refine_decode"]
    detector_options.refine_pose = settings["apriltag3"]["refine_pose"]
    detector_options.debug = settings["apriltag3"]["debug"]
    detector_options.quad_contours = settings["apriltag3"]["quad_contours"]

elif detector == "wpilib":
    pass

# Preview Window
logger_enabled = settings["preview"]["enabled"]
video_display_fps = settings["preview"]["show_fps"]
stream_quality = int(os.environ.get("STREAM_QUALITY", settings["preview"]["stream_quality"]))
log_quality = int(os.environ.get("LOG_QUALITY", settings["preview"]["log_quality"]))
stream_res = settings["preview"]["max_stream_res"]

test_video = os.environ.get("TEST_VIDEO", settings["test_video"])

# not constants
last_frame = None
detections = None
fps = [0 for x in range(10)]
poses = None
new_data = False

# Define apriltag locations
apriltag_size = 0.1524  # meters

m = open(settings["map"], 'r')
tags = json.load(m)["tags"]
m.close()

tag_world_coords = {}

pose_estimation_mode = os.environ.get("SOLVEPNP_MODE", settings["solvepnp_method"])
capture_mode = os.environ.get("CAPTURE_METHOD", settings["capture"])

for tag in tags:
    tag_pose = Pose3d(Translation3d(tag["pose"]["translation"]["x"],
                                    tag["pose"]["translation"]["y"],
                                    tag["pose"]["translation"]["z"]),
                      Rotation3d(Quaternion(tag["pose"]["rotation"]["quaternion"]["W"],
                                            tag["pose"]["rotation"]["quaternion"]["X"],
                                            tag["pose"]["rotation"]["quaternion"]["Y"],
                                            tag["pose"]["rotation"]["quaternion"]["Z"])))
    tag_world_coords[tag["ID"]] = TagCoordinates(tag_pose, apriltag_size)


# condense config variables into a json
def is_serializable(v):
    try:
        json.dumps(v)
        return True
    except (TypeError, OverflowError):
        return False


# Filter out non-serializable items, functions, built-ins, and modules
log_exclude = ["settings", "tag", "last_frame", "detections", "poses", "new_data", "log_exclude", "fps", "tags"]
module_vars = {
    k: v for k, v in globals().items()
    if k not in log_exclude and not k.startswith('__') and not callable(v) and is_serializable(v)
}

config_json = json.dumps(module_vars, indent=4)
