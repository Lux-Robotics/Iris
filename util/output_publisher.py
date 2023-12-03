import math

import ntcore

import util.config as config
from util.vision_types import Pose

from util.config import version


class NTPublisher:
    # Initiate Connection
    def __init__(self, ip: str) -> None:
        ntcore.NetworkTableInstance.getDefault().setServer(ip)
        ntcore.NetworkTableInstance.getDefault().startClient4("Perception")
        self.output_table = ntcore.NetworkTableInstance.getDefault().getTable(
            "/Perception/" + config.device_id)
        self.observations0_pub = self.output_table.getDoubleArrayTopic("observations0").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True))
        self.observations1_pub = self.output_table.getDoubleArrayTopic("observations1").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True))
        self.errors_pub = self.output_table.getDoubleArrayTopic("errors").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True))
        self.fps_pub = self.output_table.getDoubleTopic("fps").publish()
        self.tags_pub = self.output_table.getIntegerTopic("tags").publish()
        self.version_pub = self.output_table.getStringTopic("version").publish()
        self.version_pub.set(version)

    def publish_data(self, pose0: Pose, pose1: Pose, tags: int, timestamp: float) -> None:
        errors = []
        observation_data = []
        if pose0 is not None:
            wpi_pose0 = pose0.get_wpilib()
            observation_data.append(wpi_pose0.translation().X())
            observation_data.append(wpi_pose0.translation().Y())
            observation_data.append(wpi_pose0.translation().Z())
            observation_data.append(wpi_pose0.rotation().getQuaternion().W())
            observation_data.append(wpi_pose0.rotation().getQuaternion().X())
            observation_data.append(wpi_pose0.rotation().getQuaternion().Y())
            observation_data.append(wpi_pose0.rotation().getQuaternion().Z())
            errors.append(pose0.error)
        try:
            fps = 9 / (config.fps[-1] - config.fps[-10])
        except:
            fps = 0
        observation_data_2 = []
        if pose1 is not None:
            wpi_pose1 = pose1.get_wpilib()
            observation_data_2.append(wpi_pose1.translation().X())
            observation_data_2.append(wpi_pose1.translation().Y())
            observation_data_2.append(wpi_pose1.translation().Z())
            observation_data_2.append(wpi_pose1.rotation().getQuaternion().W())
            observation_data_2.append(wpi_pose1.rotation().getQuaternion().X())
            observation_data_2.append(wpi_pose1.rotation().getQuaternion().Y())
            observation_data_2.append(wpi_pose1.rotation().getQuaternion().Z())
            errors.append(pose1.error)

        self.observations0_pub.set(observation_data, math.floor(timestamp * 1000000))
        self.observations1_pub.set(observation_data_2, math.floor(timestamp * 1000000))
        self.errors_pub.set(errors, math.floor(timestamp * 1000000))
        self.fps_pub.set(fps, math.floor(timestamp * 1000000))
        self.tags_pub.set(int(tags), math.floor(timestamp * 1000000))
