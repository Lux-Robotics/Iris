import math
import time
from typing import List

import ntcore

import util.state as state
from util.state import settings
from util.vision_types import Pose, TagObservation


class NTInterface:
    # Initiate Connection
    def __init__(self, ip: str) -> None:
        ntcore.NetworkTableInstance.getDefault().setServer(ip)
        ntcore.NetworkTableInstance.getDefault().startClient4("Perception")
        self.output_table = ntcore.NetworkTableInstance.getDefault().getTable(
            "/Perception/" + settings.device_id
        )
        self.observations0_pub = self.output_table.getDoubleArrayTopic(
            "observations0"
        ).publish(ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True))
        self.observations1_pub = self.output_table.getDoubleArrayTopic(
            "observations1"
        ).publish(ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True))
        self.errors_pub = self.output_table.getDoubleArrayTopic("errors").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True)
        )
        self.tags_pub = self.output_table.getIntegerArrayTopic("tag_ids").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True)
        )
        self.fps_pub = self.output_table.getDoubleTopic("fps").publish()
        self.version_pub = self.output_table.getStringTopic("version").publish()
        self.version_pub.set(state.version)

        self.config_table = ntcore.NetworkTableInstance.getDefault().getTable(
            "/Perception/config"
        )
        self.tagignore_sub = self.config_table.getIntegerArrayTopic(
            "ignored_tags"
        ).subscribe([])

        fms_data = ntcore.NetworkTableInstance.getDefault().getTable("/FMSInfo")
        self.control_data_sub = fms_data.getIntegerTopic("FMSControlData").subscribe(0)

    def publish_data(
        self, pose0: Pose, pose1: Pose, tags: List[TagObservation], timestamp: float
    ) -> None:
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
            fps = state.fps
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
        self.tags_pub.set([tag.tag_id for tag in tags], math.floor(timestamp * 1000000))

    def get_states(self):
        state.ignored_tags = self.tagignore_sub.get([])

        control_data = self.control_data_sub.get(0)
        (
            ds_attached,
            fms_attached,
            emergency_stopped,
            test_enabled,
            auto_enabled,
            robot_enabled,
        ) = [(control_data & (1 << bit)) > 0 for bit in range(5, -1, -1)]

        if robot_enabled:
            state.robot_last_enabled = time.time()
