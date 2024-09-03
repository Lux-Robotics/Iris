import cv2

import util.state as state
from util.vision_types import TagObservation


def find_corners(image):
    detected_corners, ids, _ = cv2.aruco.detectMarkers(
        image, state.aruco_dict, parameters=state.aruco_detection_params
    )
    if len(detected_corners) == 0:
        return []
    return [
        TagObservation(tag_id[0], corners)
        for corners, tag_id in zip(detected_corners, ids)
    ]
