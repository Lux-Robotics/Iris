import json
import numpy as np
import cv2


f = open("config.json", 'r')
settings = json.load(f)
f.close()


c = open(settings["calibration"], 'r')
calibration = json.load(c)
camera_matrix = np.array(calibration["cameraMatrix"])
dist_coeffs = np.array(calibration["distCoeffs"])
resolution = tuple(calibration["resolution"])
c.close()


# Setup detection params
detection_params = cv2.aruco.DetectorParameters()
detection_params.useAruco3Detection = settings["aruco"]["aruco3"]
detection_params.aprilTagQuadDecimate = settings["aruco"]["decimate"]

match settings["aruco"]["corner_refinement"]:
    case 0:
        detection_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_NONE
    case 1:
        detection_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        detection_params.cornerRefinementWinSize = 11


apriltag_size = 0.1524  # meters
