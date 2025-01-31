import math
import time
from typing import List

import ntcore
from ntcore import NetworkTableInstance, Publisher, Subscriber, Topic
from wpimath.geometry import Pose3d, Translation2d

import util.state as state
import util.v4l2_ctrls
from util.snapshot_manager import list_snapshots
from util.state import Platform, save_settings
from util.vision_types import IrisPoseEstimationResult, IrisTarget, Pose, TagObservation


def _add_attribute(topic: Topic, default_value: any) -> tuple[Subscriber, Publisher]:
    """
    Util for creating a NetworkTables subscriber and publisher with a default value
    """
    sub: Subscriber = topic.subscribe(default_value)
    pub: Publisher = topic.publish(
        ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=False)
    )
    pub.set(default_value)
    return sub, pub


# TODO: change to REST api
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
        if state.current_platform != Platform.DEV:
            inst.setServer(ip)
            inst.startClient4("iris")
        else:
            inst = NTListener.inst
        self.output_table = inst.getTable("/iris/" + state.device_id)

        self.pose_est_pub = self.output_table.getStructTopic(
            "cameraPose", IrisPoseEstimationResult
        ).publish(ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=False))

        self.targets_pub = self.output_table.getStructArrayTopic(
            "targets", IrisTarget
        ).publish(ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=False))

        self.fps_pub = self.output_table.getDoubleTopic("fps").publish()
        _, self.version_pub = _add_attribute(
            self.output_table.getStringTopic("version"), state.version
        )

        self.config_table = inst.getTable("/Iris/config")
        self.tagignore_sub = self.config_table.getIntegerArrayTopic(
            "ignored_tags"
        ).subscribe([])

        self.control_data_sub = (
            inst.getTable("/FMSInfo").getIntegerTopic("FMSControlData").subscribe(0)
        )
        self.corner_data_pub = self.output_table.getStructArrayTopic(
            "corners", Translation2d
        ).publish(ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=False))

    def publish_data(
        self,
        pose0: Pose,
        pose1: Pose,
        targets: List[IrisTarget],
        tags: List[TagObservation],
        timestamp: float,
    ) -> None:
        if pose0 is not None:
            self.pose_est_pub.set(
                IrisPoseEstimationResult(
                    pose0.get_wpilib(),
                    pose0.error,
                    pose1.get_wpilib() if pose1 is not None else Pose3d(),
                    pose1.error if pose1 is not None else -1,
                ),
                math.floor(timestamp * 1000000),
            )
        self.fps_pub.set(state.fps, math.floor(timestamp * 1000000))
        self.targets_pub.set(targets, math.floor(timestamp * 1000000))
        corners = []
        for t in tags:
            for c in t.corners[0]:
                corners.append(Translation2d(c[0], c[1]))
        self.corner_data_pub.set(corners, math.floor(timestamp * 1000000))

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


# TODO: need better name
# Local NT server
class NTListener:
    inst = ntcore.NetworkTableInstance.create()

    def __init__(self):
        inst = self.inst
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
        _, self.uptime_pub = _add_attribute(inst.getIntegerTopic("uptime"), 0)

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
        self.sharpen_sub, self.sharpen_pub = _add_attribute(
            inst.getDoubleTopic("decode_sharpen"),
            state.settings.apriltag3.decode_sharpening,
        )

        self.decision_margin_sub, self.decision_margin_pub = _add_attribute(
            inst.getIntegerTopic("decision_margin"),
            state.settings.apriltag3.decision_margin,
        )

        self.n_threads_sub, self.n_threads_pub = _add_attribute(
            inst.getIntegerTopic("threads"), state.settings.apriltag3.threads
        )

        _, self.snapshots_pub = _add_attribute(
            inst.getStringArrayTopic("snapshots"), list_snapshots()
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
            self.sharpen_sub,
            ntcore.EventFlags.kValueAll,
            lambda event: (
                setattr(
                    state.settings.apriltag3,
                    "decode_sharpening",
                    event.data.value.getDouble(),
                ),
                setattr(state, "detector_update_needed", True),
                save_settings(),
            ),
        )
        inst.addListener(
            self.decision_margin_sub,
            ntcore.EventFlags.kValueAll,
            lambda event: (
                setattr(
                    state.settings.apriltag3,
                    "decision_margin",
                    event.data.value.getInteger(),
                ),
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

    def periodic(self, timestamp: float):
        self.update_data(timestamp)
