import cv2
import numpy as np
import util.constants as config
from util.vision_types import TagObservation

# Detect tags in the 16h5 family
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_16h5)


def find_corners(image):
    detected_corners, ids, _ = cv2.aruco.detectMarkers(image, aruco_dict, parameters=config.detection_params)
    if len(detected_corners) == 0:
        return []
    return [TagObservation(tag_id[0], corners) for corners, tag_id in zip(detected_corners, ids)]


def draw_detections(image, detections):
    # Draw corners on the image
    for detection in detections:
        cv2.aruco.drawDetectedMarkers(image, np.array([detection.corners]), np.array([[detection.tag_id]]))
    return image
