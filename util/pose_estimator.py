# work in progress
import cv2
import numpy as np

import util.load_config as constants


def solvepnp_singletag(detections):
    poses = {}
    for ids, corners in detections:
        corners = corners.reshape((4, 2))
        world_coords = np.array([
            [-constants.apriltag_size / 2, constants.apriltag_size / 2, 0],
            [constants.apriltag_size / 2, constants.apriltag_size / 2, 0],
            [constants.apriltag_size / 2, -constants.apriltag_size / 2, 0],
            [-constants.apriltag_size / 2, -constants.apriltag_size / 2, 0]
        ])

        _, rvec, tvec = cv2.solvePnP(world_coords, corners, constants.camera_matrix, distCoeffs=constants.dist_coeffs, flags=cv2.SOLVEPNP_IPPE_SQUARE)
        poses[ids[0]] = [rvec, tvec]
        # print(poses)

    # print(poses)
    return poses
