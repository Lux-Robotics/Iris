# work in progress
import cv2
import numpy as np

import util.config as constants


def solvepnp_singletag(detections):
    poses = {}
    for detection in detections:
        corners = detection.corners.reshape((4, 2))
        world_coords = np.array([
            [-constants.apriltag_size / 2, constants.apriltag_size / 2, 0],
            [constants.apriltag_size / 2, constants.apriltag_size / 2, 0],
            [constants.apriltag_size / 2, -constants.apriltag_size / 2, 0],
            [-constants.apriltag_size / 2, -constants.apriltag_size / 2, 0]
        ])

        _, rvec, tvec = cv2.solvePnP(world_coords, corners, constants.camera_matrix, distCoeffs=constants.dist_coeffs, flags=cv2.SOLVEPNP_IPPE_SQUARE)
        poses[detection.tag_id] = [rvec, tvec]

    return poses
