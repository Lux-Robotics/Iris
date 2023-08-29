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
    for ids, corners in detections:
        corners = corners.reshape((4, 2))
        corners = corners.astype(int)
        # for corner in corners:
            # cv2.circle(image, tuple(corner), 10, (0, 255, 0), -1)  # Draw a green circle at the corner
        cv2.line(image, corners[0], corners[1], (0, 255, 0), 1)
        cv2.line(image, corners[1], corners[2], (0, 255, 0), 1)
        cv2.line(image, corners[2], corners[3], (0, 255, 0), 1)
        cv2.line(image, corners[3], corners[0], (0, 255, 0), 1)
        cv2.putText(image, "ID:" + str(ids[0]),
                    (corners[2][0], corners[2][1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
        # print("[INFO] ArUco marker ID: {}".format(ids))
    return image
