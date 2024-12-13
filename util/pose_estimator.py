import cv2
import numpy as np

import util.state as state
from util.vision_types import IrisTarget, Pose, TagObservation, TargetAngle


def get_angle_offset(x: float, y: float):
    K = np.array(state.settings.calibration.cameraMatrix)
    D = np.array(state.settings.calibration.distCoeffs)

    # Undistort the image points
    undistorted_points = cv2.undistortPoints(np.array([[x, y]]), K, D, P=K)

    # Camera intrinsic parameters
    fx = K[0, 0]
    fy = K[1, 1]
    cx = K[0, 2]
    cy = K[1, 2]

    x = undistorted_points[0, 0, 0]
    y = undistorted_points[0, 0, 1]

    angle_x = np.arctan((x - cx) / fx)
    angle_y = np.arctan((y - cy) / fy)

    return angle_x, angle_y


def solvepnp_singletag(detections):
    if len(detections) == 0:
        return ()
    for detection in detections:
        if detection.tag_id not in state.tag_world_coords:
            continue
        if detection.tag_id in state.ignored_tags:
            continue
        corners = detection.corners.reshape((4, 2))
        world_coords = state.tag_world_coords[detection.tag_id].get_corners()

        _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
            world_coords,
            corners,
            np.array(state.settings.calibration.cameraMatrix),
            distCoeffs=np.array(state.settings.calibration.distCoeffs),
            flags=cv2.SOLVEPNP_AP3P,
        )
        if len(rvecs) > 1:
            return Pose(rvecs[0], tvecs[0], errors[0]), Pose(
                rvecs[1], tvecs[1], errors[1]
            )
        else:
            return (Pose(rvecs[0], tvecs[0], errors[0]),)


def get_tag_angle_offset(detection: TagObservation) -> IrisTarget:
    poses = solvepnp_singletag([detection])
    center_point = np.mean(detection.corners.reshape((4, 2)), axis=0)
    t_x, t_y = get_angle_offset(center_point[0], center_point[1])
    corners = [get_angle_offset(c[0], c[1]) for c in detection.corners[0]]
    return IrisTarget(
        detection.tag_id,
        poses[0].get_transform(),
        poses[0].error,
        poses[1].get_transform() if len(poses) > 1 else None,
        poses[1].error if len(poses) > 1 else -1,
        TargetAngle(t_x, t_y),
        TargetAngle(corners[0][0], corners[0][1]),
        TargetAngle(corners[1][0], corners[1][1]),
        TargetAngle(corners[2][0], corners[2][1]),
        TargetAngle(corners[3][0], corners[3][1]),
    )


def solvepnp_multitag(detections):
    corners = np.empty((0, 2))
    world_coords = np.empty((0, 3))

    for detection in detections:
        corners = np.vstack((corners, detection.corners.reshape((4, 2))))
        world_coords = np.vstack(
            (world_coords, state.tag_world_coords[detection.tag_id].get_corners())
        )

    _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
        world_coords,
        corners,
        np.array(state.settings.calibration.cameraMatrix),
        distCoeffs=np.array(state.settings.calibration.distCoeffs),
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
            (world_coords, state.tag_world_coords[detection.tag_id].get_corners())
        )

    retval, rvec, tvec, inliers = cv2.solvePnPRansac(
        world_coords,
        corners,
        np.array(state.settings.calibration.cameraMatrix),
        distCoeffs=np.array(state.settings.calibration.distCoeffs),
        flags=cv2.SOLVEPNP_SQPNP,
    )

    if retval:
        return (Pose(rvec, tvec, 0),)
    else:
        return ()
