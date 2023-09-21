import math
from dataclasses import dataclass
import numpy as np
from wpimath.geometry import *
import cv2

@dataclass(frozen=True)
class TagObservation:
    tag_id: int
    corners: np.ndarray[np.float64]


@dataclass(frozen=True)
class Pose:
    rvec: np.ndarray[np.float64]
    tvec: np.ndarray[np.float64]

    def get_wpilib(self):
        # shift coordinate system
        tvec = np.array([-self.tvec[2], self.tvec[0], self.tvec[1]])
        rvec = np.array([self.rvec[2], -self.rvec[0], self.rvec[1]])
        return Pose3d(
            Translation3d(tvec[0][0], tvec[1][0], tvec[2][0]),
            Rotation3d(cv2.Rodrigues(rvec)[0]))


class TagCoordinates:
    def __init__(self, tag_pos: Pose3d, tag_size):
        transform = Transform3d(
            tag_pos.translation(),
            tag_pos.rotation())
        self.corners = [Pose3d(0, -tag_size / 2, tag_size / 2, Rotation3d()),
                        Pose3d(0, tag_size / 2, tag_size / 2, Rotation3d()),
                        Pose3d(0, tag_size / 2, -tag_size / 2, Rotation3d()),
                        Pose3d(0, -tag_size / 2, -tag_size / 2, Rotation3d())]
        self.corners = [corner.transformBy(transform) for corner in self.corners]
        [print(corner.X(), corner.Y(), corner.Z()) for corner in self.corners]

    def get_corners(self):
        return np.array([
            [corner.translation().Y(), corner.translation().Z(), corner.translation().X()] for corner in self.corners
        ])


def invert_pose(rvec, tvec):
    # Calculate the rotation matrix R from rvec
    R, _ = cv2.Rodrigues(rvec)

    # Calculate the inverse rotation matrix
    R = R.T

    # Calculate the inverse translation vector
    tvec = -np.dot(R, tvec)

    # Create a 4x4 transformation matrix T
    T = np.eye(4, dtype=R.dtype)

    # Copy the rotation matrix R into the top-left 3x3 block of T
    T[0:3, 0:3] = R

    # Copy the translation vector tvec into the rightmost column of T
    T[0:3, 3] = tvec.reshape(3, )

    # Fill the last row of T
    T[3, :] = [0, 0, 0, 1]


    R = T[0:3, 0:3]

    # Extract the translation vector tvec from the rightmost column of T
    tvec = T[0:3, 3].reshape(3, 1)

    tvec = np.array([-tvec[0], tvec[1], -tvec[2]])

    # Calculate the rotation vector rvec from R
    rvec, _ = cv2.Rodrigues(R)

    return rvec, tvec