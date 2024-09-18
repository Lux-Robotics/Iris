import math
import time
from typing import List

from wpimath.geometry import Pose3d

from util.state import save_settings
from util.vision_types import Pose, TagObservation, IrisPose, IrisTarget
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
        # inst = NTListener.inst
        inst.setServer(ip)
        inst.startClient4("Iris")
        self.output_table = inst.getTable("/Iris/" + state.device_id)
        _, self.errors_pub = _add_attribute(
            self.output_table.getDoubleTopic("reprojection_error"), 0.0
        )

        self.camera_pose_pub = self.output_table.getStructTopic(
            "camera_pose", Pose3d
        ).publish(ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=False))

        self.targets_pub = self.output_table.getStructArrayTopic(
            "targets", IrisTarget
        ).publish(ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=False))

        _, self.tags_pub = _add_attribute(
            self.output_table.getIntegerArrayTopic("tags_seen"), []
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
        self,
        pose0: Pose,
        pose1: Pose,
        targets: List[IrisTarget],
        tags: List[TagObservation],
        timestamp: float,
    ) -> None:
        if pose0 is not None:
            self.camera_pose_pub.set(
                pose0.get_wpilib(), math.floor(timestamp * 1000000)
            )
            self.errors_pub.set(pose0.error, math.floor(timestamp * 1000000))
        self.fps_pub.set(state.fps, math.floor(timestamp * 1000000))
        self.tags_pub.set([tag.tag_id for tag in tags], math.floor(timestamp * 1000000))
        self.targets_pub.set(targets, math.floor(timestamp * 1000000))

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
    # inst = ntcore.NetworkTableInstance.create()

    def __init__(self):
        inst = ntcore.NetworkTableInstance.create()
        # inst = self.inst
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
        _, self.calibration_progress_pub = _add_attribute(
            inst.getIntegerTopic("calibrationProgress"), 0
        )
        _, self.calibration_failed_pub = _add_attribute(
            inst.getIntegerTopic("calibrationFailed"), -1
        )
        _, self.snapshots_pub = _add_attribute(
            inst.getStringArrayTopic("snapshots"), state.snapshots
        )

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
        self.calibration_failed_pub.set(state.calibration_progress)
        self.snapshots_pub.set(state.snapshots)

    def periodic(self, timestamp: float):
        self.update_data(timestamp)
