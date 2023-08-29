import cv2
import numpy as np
import util.constants as config
# from util.vision_types import TagObservation

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_16h5)
aruco_params = cv2.aruco.DetectorParameters()
aruco_params.useAruco3Detection = False
aruco_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX


def find_corners(image):
    corners, ids, _ = cv2.aruco.detectMarkers(image, aruco_dict, parameters=aruco_params)
    if len(corners) == 0:
        return np.array([]), np.array([])
    return ids, corners


def draw_detections(image, detections):
    # Draw corners on the image
    for ids, corners in detections:
        corners = corners.reshape((4, 2))
        corners = corners.astype(int)
        # for corner in corners:
            # cv2.circle(image, tuple(corner), 10, (0, 255, 0), -1)  # Draw a green circle at the corner
        cv2.line(image, corners[0], corners[1], (0, 255, 0), 2)
        cv2.line(image, corners[1], corners[2], (0, 255, 0), 2)
        cv2.line(image, corners[2], corners[3], (0, 255, 0), 2)
        cv2.line(image, corners[3], corners[0], (0, 255, 0), 2)
        cv2.putText(image, "ID:" + str(ids[0]),
                    (corners[2][0], corners[2][1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
        # print("[INFO] ArUco marker ID: {}".format(ids))
    return image
