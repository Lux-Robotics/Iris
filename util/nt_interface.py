import math
import time
from typing import List

from util.state import save_settings
from util.vision_types import Pose, TagObservation
import ntcore
from ntcore import Topic, Publisher, Subscriber, NetworkTableInstance

import util.v4l2_ctrls
import util.state as state


def _add_attribute(topic: Topic, default_value: any) -> tuple[Subscriber, Publisher]:
    sub: Subscriber = topic.subscribe(default_value)
    pub: Publisher = topic.publish(
        ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=False)
    )
    pub.set(default_value)
    return sub, pub


def update_server_address(event):
    team_number = event.data.value.getInteger()
    state.settings.team_number = team_number
    NetworkTableInstance.getDefault().setServer(state.get_server_ip())
    state.logger.info("Set server to '" + state.get_server_ip() + "'")
    state.save_settings()


class NTInterface:
    # Initiate Connection
    def __init__(self, ip: str) -> None:
        inst = NetworkTableInstance.getDefault()
        inst.setServer(ip)
        inst.startClient4("Iris")
        self.output_table = inst.getTable("/Iris/" + state.device_id)
        _, self.observations0_pub = _add_attribute(
            self.output_table.getDoubleArrayTopic("observations0"), []
        )
        _, self.observations1_pub = _add_attribute(
            self.output_table.getDoubleArrayTopic("observations1"), []
        )
        _, self.errors_pub = _add_attribute(
            self.output_table.getDoubleArrayTopic("errors"), []
        )
        _, self.tags_pub = _add_attribute(
            self.output_table.getIntegerArrayTopic("tag_ids"), []
        )
        self.fps_pub = self.output_table.getDoubleTopic("fps").publish()
        _, self.version_pub = _add_attribute(
            inst.getStringTopic("version"), state.version
        )

        self.config_table = inst.getTable("/Iris/config")
        self.tagignore_sub = self.config_table.getIntegerArrayTopic(
            "ignored_tags"
        ).subscribe([])

        self.control_data_sub = (
            inst.getTable("/FMSInfo").getIntegerTopic("FMSControlData").subscribe(0)
        )

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


class NTListener:
    def __init__(self):
        inst = ntcore.NetworkTableInstance.create()
        inst.startServer()

        # device config
        self.team_sub, self.team_pub = _add_attribute(
            inst.getIntegerTopic("teamNumber"), state.settings.team_number
        )

        _, self.fps_pub = _add_attribute(inst.getDoubleTopic("fps"), 0)
        _, self.version_pub = _add_attribute(
            inst.getStringTopic("version"), state.version
        )
        _, self.git_hash_pub = _add_attribute(
            inst.getStringTopic("gitCommitHash"), state.git_hash
        )
        _, self.hardware_info = _add_attribute(
            inst.getStringTopic("hardwareInfo"), "Unknown"
        )
        _, self.uptime_pub = _add_attribute(
            inst.getIntegerTopic("uptime"), 0
        )  # TODO: fix

        # camera settings
        self.brightness_sub, self.brightness_pub = _add_attribute(
            inst.getIntegerTopic("brightness"), state.settings.camera.brightness
        )
        self.exposure_sub, self.exposure_pub = _add_attribute(
            inst.getIntegerTopic("exposure"), state.settings.camera.exposure
        )
        self.gain_sub, self.gain_pub = _add_attribute(
            inst.getIntegerTopic("gain"), state.settings.camera.gain
        )

        # apriltag settings
        self.detector_sub, self.detector_pub = _add_attribute(
            inst.getStringTopic("detector"), state.settings.detector
        )
        self.family_sub, self.family_pub = _add_attribute(
            inst.getStringTopic("tagFamily"), state.settings.apriltag3.families
        )
        self.decimate_sub, self.decimate_pub = _add_attribute(
            inst.getDoubleTopic("decimate"), state.settings.apriltag3.quad_decimate
        )
        self.blur_sub, self.blur_pub = _add_attribute(
            inst.getDoubleTopic("blur"), state.settings.apriltag3.quad_sigma
        )
        self.n_threads_sub, self.n_threads_pub = _add_attribute(
            inst.getIntegerTopic("threads"), state.settings.apriltag3.threads
        )

        # calibration
        _, self.calibration_progress_pub = _add_attribute(inst.getIntegerTopic("calibrationProgress"), 0)

        # TODO: switch to MultiSubscriber?
        inst.addListener(
            self.detector_sub,
            ntcore.EventFlags.kValueAll,
            lambda event: (
                setattr(state.settings, "detector", event.data.value.getString()),
                setattr(state, "detector_update_needed", True),
                save_settings(),
            ),
        )
        inst.addListener(
            self.family_sub,
            ntcore.EventFlags.kValueAll,
            lambda event: (
                setattr(
                    state.settings.apriltag3, "families", event.data.value.getString()
                ),
                setattr(state, "detector_update_needed", True),
                save_settings(),
            ),
        )
        inst.addListener(
            self.decimate_sub,
            ntcore.EventFlags.kValueAll,
            lambda event: (
                setattr(
                    state.settings.apriltag3,
                    "quad_decimate",
                    event.data.value.getDouble(),
                ),
                setattr(state, "detector_update_needed", True),
                save_settings(),
            ),
        )
        inst.addListener(
            self.blur_sub,
            ntcore.EventFlags.kValueAll,
            lambda event: (
                setattr(
                    state.settings.apriltag3,
                    "quad_sigma",
                    event.data.value.getDouble(),
                ),
                setattr(state, "detector_update_needed", True),
                save_settings(),
            ),
        )
        inst.addListener(
            self.n_threads_sub,
            ntcore.EventFlags.kValueAll,
            lambda event: (
                setattr(
                    state.settings.apriltag3, "threads", event.data.value.getInteger()
                ),
                setattr(state, "detector_update_needed", True),
                save_settings(),
            ),
        )
        inst.addListener(
            self.team_sub,
            ntcore.EventFlags.kValueAll,
            update_server_address,
        )

        inst.addListener(
            self.gain_sub, ntcore.EventFlags.kValueAll, util.v4l2_ctrls.update_gain
        )

        inst.addListener(
            self.brightness_sub,
            ntcore.EventFlags.kValueAll,
            util.v4l2_ctrls.update_brightness,
        )
        inst.addListener(
            self.exposure_sub,
            ntcore.EventFlags.kValueAll,
            util.v4l2_ctrls.update_exposure,
        )

    # TODO: add timestamps, latency
    def update_data(self, timestamp: float):
        # Update fps
        self.fps_pub.set(state.fps)
        self.uptime_pub.set(int(state.frame_times[-1] - state.frame_times[0]))
        self.calibration_progress_pub.set(state.calibration_progress)

    def periodic(self, timestamp: float):
        self.update_data(timestamp)
