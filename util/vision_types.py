import dataclasses
import math
from dataclasses import dataclass
from typing import Any

import numpy as np
import wpiutil.wpistruct
from numpy import dtype, ndarray
from wpimath.geometry import Pose3d, Quaternion, Rotation3d, Transform3d, Translation3d


@wpiutil.wpistruct.make_wpistruct(name="TargetAngle")
@dataclasses.dataclass
class TargetAngle:
    x: wpiutil.wpistruct.double
    y: wpiutil.wpistruct.double


@wpiutil.wpistruct.make_wpistruct(name="IrisTarget")
@dataclasses.dataclass
class IrisTarget:
    id: wpiutil.wpistruct.int32
    primaryTransform: Transform3d
    primaryReprojError: wpiutil.wpistruct.double
    secondaryTransform: Transform3d
    secondaryReprojError: wpiutil.wpistruct.double
    center: TargetAngle
    c0: TargetAngle
    c1: TargetAngle
    c2: TargetAngle
    c3: TargetAngle


@wpiutil.wpistruct.make_wpistruct(name="IrisPoseEstimationResult")
@dataclasses.dataclass
class IrisPoseEstimationResult:
    primaryPose: Pose3d
    primaryReprojError: wpiutil.wpistruct.double
    secondaryPose: Pose3d
    secondaryReprojError: wpiutil.wpistruct.double


@dataclass(frozen=True)
class TagObservation:
    tag_id: int
    corners: np.ndarray[np.float64]


@dataclass(frozen=True)
class Pose:
    rvec: np.ndarray[np.float64]
    tvec: np.ndarray[np.float64]
    error: float

    def get_object_pose(self) -> Pose3d:
        pose = self.get_wpilib()
        pose = pose.transformBy(
            Transform3d(Translation3d(), Rotation3d(Quaternion(-0.5, 0.5, -0.5, 0.5)))
        )
        return pose

    def get_wpilib(self) -> Pose3d:
        # shift coordinate system
        tvec = np.array([self.tvec[2], -self.tvec[0], -self.tvec[1]])

        pose = Pose3d(
            Translation3d(tvec[0][0], tvec[1][0], tvec[2][0]),
            Rotation3d(
                np.array([self.rvec[2][0], -self.rvec[0][0], -self.rvec[1][0]]),
                math.sqrt(
                    math.pow(self.rvec[0][0], 2)
                    + math.pow(self.rvec[1][0], 2)
                    + math.pow(self.rvec[2][0], 2)
                ),
            ),
        )

        # solvepnp returns pose to object, invert to get camera pose
        target_pose = Transform3d(pose.translation(), pose.rotation())
        world_pose = target_pose.inverse()
        return Pose3d(world_pose.translation(), world_pose.rotation())

    def get_transform(self) -> Transform3d:
        target_pose = self.get_object_pose()
        return Transform3d(target_pose.translation(), target_pose.rotation())


class TagCoordinates:
    def __init__(self, tag_pos: Pose3d, tag_size):
        self.corners = [
            Transform3d(Translation3d(0, tag_size / 2, -tag_size / 2), Rotation3d()),
            Transform3d(Translation3d(0, -tag_size / 2, -tag_size / 2), Rotation3d()),
            Transform3d(Translation3d(0, -tag_size / 2, tag_size / 2), Rotation3d()),
            Transform3d(Translation3d(0, tag_size / 2, tag_size / 2), Rotation3d()),
        ]
        self.corners = [tag_pos.transformBy(corner) for corner in self.corners]

    def get_corners(self) -> ndarray[Any, dtype[Any]]:
        return np.array(
            [
                [
                    -corner.translation().Y(),
                    -corner.translation().Z(),
                    corner.translation().X(),
                ]
                for corner in self.corners
            ]
        )
