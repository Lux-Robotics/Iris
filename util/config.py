import json
import numpy as np
import cv2
import apriltag
from wpimath.geometry import *
from util.vision_types import TagCoordinates

f = open("config.json", 'r')
settings = json.load(f)
f.close()

# Camera config
camera_auto_exposure = int(settings["camera"]["auto_exposure"])
camera_exposure = settings["camera"]["manual_exposure"]
camera_gain = settings["camera"]["gain"]

c = open(settings["camera"]["calibration"], 'r')
calibration = json.load(c)
camera_matrix = np.array(calibration["cameraMatrix"])
dist_coeffs = np.array(calibration["distCoeffs"])
resx, resy = tuple(calibration["resolution"])
c.close()

# networktables
use_nt = settings["use_networktables"]
device_id = settings["device_id"]

# Setup detection params
match settings["detector"]:
    case "aruco":
        detection_params = cv2.aruco.DetectorParameters()
        detection_params.useAruco3Detection = settings["aruco"]["aruco3"]
        detection_params.aprilTagQuadDecimate = settings["aruco"]["decimate"]

        match settings["aruco"]["corner_refinement"]:
            case "none":
                detection_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_NONE
            case "subpix":
                detection_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
                detection_params.cornerRefinementWinSize = 11
    case "apriltag3":
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

# Preview Window
preview = settings["preview"]["enabled"]
preview_fps = settings["preview"]["show_fps"]
preview_pose = settings["preview"]["show_transform"]
stream_quality = settings["preview"]["stream_quality"]
stream_res = settings["preview"]["max_stream_res"]
stream_port = settings["preview"]["stream_port"]

test_video = settings["test_video"]

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

pose_estimation_mode = settings["solvepnp_method"]
capture_mode = settings["capture"]

for tag in tags:
    tag_pose = Pose3d(Translation3d(tag["pose"]["translation"]["x"],
                                    tag["pose"]["translation"]["y"],
                                    tag["pose"]["translation"]["z"]),
                      Rotation3d(Quaternion(tag["pose"]["rotation"]["quaternion"]["W"],
                                            tag["pose"]["rotation"]["quaternion"]["X"],
                                            tag["pose"]["rotation"]["quaternion"]["Y"],
                                            tag["pose"]["rotation"]["quaternion"]["Z"])))
    tag_world_coords[tag["ID"]] = TagCoordinates(tag_pose, apriltag_size)
