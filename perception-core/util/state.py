import json
import logging
import subprocess

import pyapriltags
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


def load_calibration(settings):
    """Hook to load calibration data into settings."""
    with open(settings.camera.calibration_file, "r") as c:
        calibration = json.load(c)
    return {"calibration": calibration}


def get_git_info():
    try:
        # Run the git command to get the latest tag description
        result = subprocess.run(
            ["git", "describe", "--tags"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        description = result.stdout.strip()
        parts = description.split("-")
        last_tagged_version = parts[0]
        current_commit = parts[2][1:]  # Remove the 'g' prefix

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
detector = pyapriltags.Detector(
    families=settings.apriltag3.families,
    nthreads=settings.apriltag3.threads,
    quad_decimate=settings.apriltag3.quad_decimate,
    refine_edges=settings.apriltag3.refine_edges,
)
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
