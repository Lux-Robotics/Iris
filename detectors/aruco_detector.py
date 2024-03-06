import cv2

import util.config as config
from util.vision_types import TagObservation

# Detect tags in the 16h5 family
# aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_16h5)
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)


def find_corners(image):
    detected_corners, ids, _ = cv2.aruco.detectMarkers(
        image, aruco_dict, parameters=config.detection_params
    )
    if len(detected_corners) == 0:
        return []
    return [
        TagObservation(tag_id[0], corners)
        for corners, tag_id in zip(detected_corners, ids)
    ]
