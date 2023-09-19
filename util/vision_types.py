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
