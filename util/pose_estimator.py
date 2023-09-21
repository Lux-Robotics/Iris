# work in progress
import cv2
import numpy as np

import util.config as config
from util.vision_types import Pose


# for testing only
def solvepnp_apriltag(detections):
    if len(detections) == 0:
        return []
    for detection in detections:
        corners = detection.corners.reshape((4, 2))
        world_coords = np.array([
            [-config.apriltag_size / 2, config.apriltag_size / 2, 0],
            [config.apriltag_size / 2, config.apriltag_size / 2, 0],
            [config.apriltag_size / 2, -config.apriltag_size / 2, 0],
            [-config.apriltag_size / 2, -config.apriltag_size / 2, 0]
        ])

        _, rvecs, tvecs, errors = cv2.solvePnPGeneric(world_coords, corners, config.camera_matrix,
                                                    distCoeffs=config.dist_coeffs,
                                                    flags=cv2.SOLVEPNP_IPPE_SQUARE)

        if len(rvecs) > 1:
            return Pose(rvecs[0], tvecs[0], errors[0]), Pose(rvecs[1], tvecs[1], errors[1])
        else:
            return (Pose(rvecs[0], tvecs[0], errors[0]), )


def solvepnp_singletag(detections):
    if len(detections) == 0:
        return []
    for detection in detections:
        corners = detection.corners.reshape((4, 2))
        world_coords = config.tag_world_coords[detection.tag_id].get_corners()

        _, rvecs, tvecs, errors = cv2.solvePnPGeneric(world_coords, corners, config.camera_matrix,
                                                    distCoeffs=config.dist_coeffs, flags=cv2.SOLVEPNP_IPPE)
        if len(rvecs) > 1:
            return Pose(rvecs[0], tvecs[0], errors[0]), Pose(rvecs[1], tvecs[1], errors[1])
        else:
            return (Pose(rvecs[0], tvecs[0], errors[0]), )


def solvepnp_multitag(detections):
    if len(detections) == 0:
        return {}
    corners = None
    world_coords = None
    for detection in detections:
        if corners is None:
            corners = detection.corners.reshape((4, 2))
        else:
            corners = np.vstack((corners, detection.corners.reshape((4, 2))))
        if world_coords is None:
            world_coords = config.tag_world_coords[detection.tag_id].get_corners()
        else:
            world_coords = np.vstack((world_coords, config.tag_world_coords[detection.tag_id].get_corners()))

    _, rvecs, tvecs, errors = cv2.solvePnPGeneric(world_coords, corners, config.camera_matrix,
                                                  distCoeffs=config.dist_coeffs, flags=cv2.SOLVEPNP_IPPE_SQUARE)
    if len(rvecs) > 1:
        return Pose(rvecs[0], tvecs[0], errors[0]), Pose(rvecs[1], tvecs[1], errors[1])
    else:
        return (Pose(rvecs[0], tvecs[0], errors[0]), )
