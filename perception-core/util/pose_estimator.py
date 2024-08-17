import cv2
import numpy as np

import util.config as config
from util.vision_types import Pose


def get_distances(detections):
    distances = []
    centerX = 0
    centerY = 0
    for detection in detections:
        corners = detection.corners.reshape((4, 2))
        world_coords = np.array(
            [
                [-config.apriltag_size / 2, config.apriltag_size / 2, 0],
                [config.apriltag_size / 2, config.apriltag_size / 2, 0],
                [config.apriltag_size / 2, -config.apriltag_size / 2, 0],
                [-config.apriltag_size / 2, -config.apriltag_size / 2, 0],
            ]
        )

        _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
            world_coords,
            corners,
            np.array(config.settings.calibration.cameraMatrix),
            distCoeffs=np.array(config.settings.calibration.distCoeffs),
            flags=cv2.SOLVEPNP_AP3P,
        )

        distance = (
            Pose(rvecs[0], tvecs[0], errors[0]).get_object_pose().translation().norm()
        )

        distances.append(Target2D(distance, theta_x, theta_y))

    return distances, centerX, centerY


def get_angle_offsets(x, y, intrinsics):
    f_x = intrinsics[0, 0]
    f_y = intrinsics[1, 1]
    c_x = intrinsics[0, 2]
    c_y = intrinsics[1, 2]

    dx = x - c_x
    dy = y - c_y

    t_x = np.degrees(np.arctan(dx / f_x))
    t_y = np.degrees(np.arctan(dy / f_y))

    return t_x, t_y


def solvepnp_singletag(detections):
    if len(detections) == 0:
        return ()
    for detection in detections:
        if detection.tag_id not in config.tag_world_coords:
            continue
        if detection.tag_id in config.ignored_tags:
            continue
        corners = detection.corners.reshape((4, 2))
        world_coords = config.tag_world_coords[detection.tag_id].get_corners()

        _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
            world_coords,
            corners,
            np.array(config.settings.calibration.cameraMatrix),
            distCoeffs=np.array(config.settings.calibration.distCoeffs),
            flags=cv2.SOLVEPNP_AP3P,
        )
        if len(rvecs) > 1:
            return Pose(rvecs[0], tvecs[0], errors[0]), Pose(
                rvecs[1], tvecs[1], errors[1]
            )
        else:
            return (Pose(rvecs[0], tvecs[0], errors[0]),)


def solvepnp_multitag(detections):
    corners = np.empty((0, 2))
    world_coords = np.empty((0, 3))

    for detection in detections:
        corners = np.vstack((corners, detection.corners.reshape((4, 2))))
        world_coords = np.vstack(
            (world_coords, config.tag_world_coords[detection.tag_id].get_corners())
        )

    _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
        world_coords,
        corners,
        np.array(config.settings.calibration.cameraMatrix),
        distCoeffs=np.array(config.settings.calibration.distCoeffs),
        flags=cv2.SOLVEPNP_SQPNP,
    )
    if len(rvecs) > 1:
        return Pose(rvecs[0], tvecs[0], errors[0]), Pose(rvecs[1], tvecs[1], errors[1])
    else:
        return (Pose(rvecs[0], tvecs[0], errors[0]),)


def solvepnp_ransac(detections):
    corners = np.empty((0, 2))
    world_coords = np.empty((0, 3))

    for detection in detections:
        corners = np.vstack((corners, detection.corners.reshape((4, 2))))
        world_coords = np.vstack(
            (world_coords, config.tag_world_coords[detection.tag_id].get_corners())
        )

    retval, rvec, tvec, inliers = cv2.solvePnPRansac(
        world_coords,
        corners,
        np.array(config.settings.calibration.cameraMatrix),
        distCoeffs=np.array(config.settings.calibration.distCoeffs),
        flags=cv2.SOLVEPNP_SQPNP,
    )

    if retval:
        return (Pose(rvec, tvec, 0),)
    else:
        return ()
