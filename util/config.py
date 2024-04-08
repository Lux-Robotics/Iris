import json
import logging
import os
import tomllib

import pyapriltags
import cv2
import numpy as np
from wpimath.geometry import *

from util.vision_types import TagCoordinates

logging.basicConfig(
    level="INFO",
    format="%(asctime)s: [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("perception")

v = open("package.json", "r")
version = json.load(v)["version"]
v.close()

f = open("config.toml", "rb")
settings = tomllib.load(f)
f.close()

# Camera config
camera_fps = settings["camera"]["fps"]

calibration_path = os.environ.get("CALIBRATION_FILE", settings["camera"]["calibration"])

c = open(calibration_path, "r")
calibration = json.load(c)
camera_matrix = np.array(calibration["cameraMatrix"])
dist_coeffs = np.array(calibration["distCoeffs"])
resx, resy = tuple(calibration["resolution"])
c.close()

# Load gstreamer pipeline
if "pipeline" in calibration:
    gstreamer_pipeline = calibration["pipeline"]
else:
    gstreamer_pipeline = settings["camera"]["pipeline"]

gstreamer_pipeline = os.environ.get("GSTREAMER_PIPELINE", gstreamer_pipeline)

# networktables
use_nt = settings["use_networktables"]
server_ip = os.environ.get("SERVER_IP", settings["server_ip"])
device_id = os.environ.get("DEVICE_ID", settings["device_id"])

# Setup detection params
detector = settings["detector"]
aruco_params = settings["aruco"]
apriltag_params = settings["apriltag3"]

if detector == "aruco":
    detection_params = cv2.aruco.DetectorParameters()
    detection_params.useAruco3Detection = aruco_params["aruco3"]
    detection_params.aprilTagQuadDecimate = aruco_params["decimate"]

    if settings["aruco"]["corner_refinement"] == "none":
        detection_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_NONE
    elif settings["aruco"]["corner_refinement"] == "subpix":
        detection_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        detection_params.relativeCornerRefinmentWinSize = aruco_params[
            "relative_refinement_window"
        ]
        detection_params.cornerRefinementWinSize = aruco_params["max_refinement_window"]

elif detector == "apriltag":
    apriltag_border = apriltag_params["border"]
    apriltag_nthreads = apriltag_params["threads"]
    apriltag_quad_decimate = apriltag_params["quad_decimate"]
    apriltag_quad_blur = apriltag_params["quad_blur"]
    apriltag_refine_edges = apriltag_params["refine_edges"]
    apriltag_refine_decode = apriltag_params["refine_decode"]
    apriltag_refine_pose = apriltag_params["refine_pose"]
    apriltag_debug = apriltag_params["debug"]
    apriltag_quad_contours = apriltag_params["quad_contours"]

elif detector == "wpilib":
    pass

# Foxglove
logger_enabled = settings["logging"]["enabled"]
stream_enabled = settings["websockets"]["enabled"]

log_quality = int(os.environ.get("LOG_QUALITY", settings["logging"]["quality"]))
stream_quality = int(
    os.environ.get("STREAM_QUALITY", settings["websockets"]["quality"])
)

stream_res = settings["websockets"]["max_res"]
log_res = settings["logging"]["max_res"]

test_video = os.environ.get("TEST_VIDEO", settings["test_video"])

# not constants
last_frame = None
filtered_detections = None
ignored_detections = None
last_frame_time = 0.0
fps = [0 for x in range(10)]
poses = []
tags2d = []
last_logged_timestamp = 0.0
new_data = False
bad_frames = 0

robot_last_enabled = False

# Define apriltag locations
apriltag_size = 0.1651  # 36h11

m = open(settings["map"], "r")
tags = json.load(m)["tags"]
m.close()

tag_world_coords = {}

ignored_tags = []

pose_estimation_mode = os.environ.get("SOLVEPNP_MODE", settings["solvepnp_method"])
capture_mode = os.environ.get("CAPTURE_METHOD", settings["capture"])

for tag in tags:
    tag_pose = Pose3d(
        Translation3d(
            tag["pose"]["translation"]["x"],
            tag["pose"]["translation"]["y"],
            tag["pose"]["translation"]["z"],
        ),
        Rotation3d(
            Quaternion(
                tag["pose"]["rotation"]["quaternion"]["W"],
                tag["pose"]["rotation"]["quaternion"]["X"],
                tag["pose"]["rotation"]["quaternion"]["Y"],
                tag["pose"]["rotation"]["quaternion"]["Z"],
            )
        ),
    )
    tag_world_coords[tag["ID"]] = TagCoordinates(tag_pose, apriltag_size)


# condense config variables into a json
def is_serializable(v):
    try:
        json.dumps(v)
        return True
    except (TypeError, OverflowError):
        return False


def to_json():
    # Filter out non-serializable items, functions, built-ins, and modules
    log_exclude = [
        "settings",
        "tag",
        "last_frame",
        "detections",
        "poses",
        "new_data",
        "log_exclude",
        "fps",
        "tags",
        "bad_frames",
        "ignored_tags",
    ]
    module_vars = {
        k: v
        for k, v in globals().items()
        if k not in log_exclude
        and not k.startswith("__")
        and not callable(v)
        and is_serializable(v)
    }

    return json.dumps(module_vars, indent=4)


config_json = to_json()
