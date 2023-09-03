import json
import numpy as np
import cv2
import apriltag


f = open("config.json", 'r')
settings = json.load(f)
f.close()


c = open(settings["calibration"], 'r')
calibration = json.load(c)
camera_matrix = np.array(calibration["cameraMatrix"])
dist_coeffs = np.array(calibration["distCoeffs"])
resx, resy = tuple(calibration["resolution"])
c.close()


# Setup detection params
match settings["detector"]:
    case "aruco":
        detection_params = cv2.aruco.DetectorParameters()
        detection_params.useAruco3Detection = settings["aruco"]["aruco3"]
        detection_params.aprilTagQuadDecimate = settings["aruco"]["decimate"]

        match settings["aruco"]["corner_refinement"]:
            case 0:
                detection_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_NONE
            case 1:
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

test_video = settings["test_video"]

# not constants
last_frame = None
detections = None
fps = [0 for x in range(10)]
poses = None

apriltag_size = 0.1524  # meters
