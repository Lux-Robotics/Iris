import json
import numpy as np


f = open("config.json", 'r')
settings = json.load(f)
f.close()

c = open(settings["calibration"], 'r')
calibration = json.load(c)
camera_matrix = calibration["cameraMatrix"]
dist_coeffs = calibration["distCoeffs"]
resolution = tuple(calibration["resolution"])
c.close()


aruco = settings["aruco"]



apriltag_size = 0.1524  # meters
