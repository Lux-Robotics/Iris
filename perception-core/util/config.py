import json
import logging

import numpy as np
import pyapriltags
from dynaconf import Dynaconf
from dynaconf.utils.boxing import DynaBox
from wpimath.geometry import *

from util.vision_types import TagCoordinates

logging.basicConfig(
    level="INFO",
    format="%(asctime)s: [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("perception")

logger.info("Logger initialized")


def load_calibration(settings):
    """Hook to load calibration data into settings."""
    with open(settings.camera.calibration_file, "r") as c:
        calibration = json.load(c)
    return {"calibration": calibration}


settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["config.toml", "version.json"],
    post_hooks=[load_calibration],
)

logger.info("Load Configuration Successful")

# Load gstreamer pipeline
if "pipeline" in settings.calibration:
    gstreamer_pipeline = settings.calibration.pipeline
    print("yes")
else:
    gstreamer_pipeline = settings["camera"]["pipeline"]

# not constants
detector = pyapriltags.Detector(
    families="tag36h11",
    nthreads=settings.apriltag3.threads,
    quad_decimate=settings.apriltag3.quad_decimate,
    refine_edges=settings.apriltag3.refine_edges,
)
detector_update_needed = False

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


# TODO: remove
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
