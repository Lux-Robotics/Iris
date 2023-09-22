import math
from dataclasses import dataclass
import numpy as np
from wpimath.geometry import *


@dataclass(frozen=True)
class TagObservation:
    tag_id: int
    corners: np.ndarray[np.float64]


@dataclass(frozen=True)
class Pose:
    rvec: np.ndarray[np.float64]
    tvec: np.ndarray[np.float64]
    error: float

    def get_wpilib(self):
        # shift coordinate system
        tvec = np.array([self.tvec[2], -self.tvec[0], -self.tvec[1]])

        pose = Pose3d(
            Translation3d(tvec[0][0], tvec[1][0], tvec[2][0]),
            Rotation3d(np.array([self.rvec[2][0], -self.rvec[0][0], -self.rvec[1][0]]),
                       math.sqrt(
                           math.pow(self.rvec[0][0], 2) + math.pow(self.rvec[1][0], 2) + math.pow(self.rvec[2][0], 2))))

        # solvepnp returns pose to object, invert to get camera pose
        target_pose = Transform3d(pose.translation(), pose.rotation())
        world_pose = target_pose.inverse()
        return Pose3d(world_pose.translation(), world_pose.rotation())


class TagCoordinates:
    def __init__(self, tag_pos: Pose3d, tag_size):
        self.corners = [Transform3d(0, -tag_size / 2, -tag_size / 2, Rotation3d()),
                        Transform3d(0, tag_size / 2, -tag_size / 2, Rotation3d()),
                        Transform3d(0, tag_size / 2, tag_size / 2, Rotation3d()),
                        Transform3d(0, -tag_size / 2, tag_size / 2, Rotation3d())]
        self.corners = [tag_pos.transformBy(corner) for corner in self.corners]

    def get_corners(self):
        return np.array([
            [-corner.translation().Y(), -corner.translation().Z(), corner.translation().X()] for corner in self.corners
        ])
