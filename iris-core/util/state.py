import json
import logging
import os
import subprocess

import cv2
import pyapriltags
from dynaconf import Dynaconf
from wpimath.geometry import *

from util.vision_types import TagCoordinates

exec_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level="INFO",
    format="%(asctime)s: [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Iris")

logger.info("Logger initialized")


def load_calibration(settings):
    """Hook to load calibration data into settings."""
    with open(os.path.join(exec_dir, settings.camera.calibration_file), "r") as c:
        calibration = json.load(c)
    return {"calibration": calibration}


def get_git_info():
    try:
        # Run the git command to get the latest tag description
        tag_result = subprocess.run(
            ["git", "describe", "--tags"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        description = tag_result.stdout.strip()
        last_tagged_version = description.split("-")[0]
        hash_result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        current_commit = hash_result.stdout.strip()

        return last_tagged_version, current_commit

    except subprocess.CalledProcessError as e:
        logging.error(
            f"An error occurred while fetching the git description: {e.stderr}"
        )
        return "Unknown", "Unknown"
    except IndexError:
        logging.error("Invalid git description format")
        return "Unknown", "Unknown"


settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["config.toml"],
    post_hooks=[load_calibration],
)

version, git_hash = get_git_info()

logger.info("Load Configuration Successful")

# Load gstreamer pipeline
if "pipeline" in settings.calibration:
    gstreamer_pipeline = settings.calibration.pipeline
else:
    gstreamer_pipeline = settings["camera"]["pipeline"]

# not constants
apriltag3_detector = pyapriltags.Detector(
    families=settings.apriltag3.families,
    nthreads=settings.apriltag3.threads,
    quad_decimate=settings.apriltag3.quad_decimate,
    refine_edges=settings.apriltag3.refine_edges,
)

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)

aruco_detection_params = cv2.aruco.DetectorParameters()
aruco_detection_params.useAruco3Detection = settings.aruco.aruco3
aruco_detection_params.aprilTagQuadDecimate = settings.apriltag3.quad_decimate
aruco_detection_params.cornerRefinementMethod = (
    cv2.aruco.CORNER_REFINE_SUBPIX
    if settings.aruco.corner_refinement
    else cv2.aruco.CORNER_REFINE_NONE
)
aruco_detection_params.relativeCornerRefinmentWinSize = (
    settings.aruco.relative_refinement_window
)
aruco_detection_params.cornerRefinementWinSize = settings.aruco.max_refinement_window

detector_update_needed = False

last_frame = None
filtered_detections = None
ignored_detections = None

last_frame_time = 0.0
fps: float = 0.0
frame_times: list[float] = []

poses = []
tags2d = []
last_logged_timestamp = 0.0
new_data = False
bad_frames = 0

robot_last_enabled = False

# Define apriltag locations
apriltag_size = 0.1651  # 36h11

m = open(os.path.join(exec_dir, settings.map), "r")
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


def get_server_ip():
    return (
        "10."
        + str(settings.team_number // 100)
        + "."
        + str(settings.team_number % 100)
        + ".2"
    )


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
