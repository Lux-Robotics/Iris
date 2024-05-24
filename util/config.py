import json
import logging

import numpy as np
from dynaconf import Dynaconf
from wpimath.geometry import *

from util.vision_types import TagCoordinates

logging.basicConfig(
    level="INFO",
    format="%(asctime)s: [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("perception")

logger.info("Logger initialized")
v = open("version.json", "r")
version = json.load(v)["version"]
v.close()

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["config.toml"],
)

logger.info("Load Configuration Successful")

c = open(settings.camera.calibration, "r")
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

m = open(settings.map, "r")
tags = json.load(m)["tags"]
m.close()

tag_world_coords = {}

ignored_tags = []

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

logger.info("Load Field Map Successful")


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
