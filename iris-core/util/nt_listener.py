import ntcore
from ntcore import Topic, Publisher, Subscriber, NetworkTableInstance

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
            inst.getDoubleTopic("brightness"), state.settings.camera.brightness
        )
        self.exposure_sub, self.exposure_pub = _add_attribute(
            inst.getDoubleTopic("exposure"), state.settings.camera.exposure
        )
        self.gain_sub, self.gain_pub = _add_attribute(
            inst.getDoubleTopic("gain"), state.settings.camera.gain
        )

        # apriltag settings
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

        # TODO: switch to MultiSubscriber?
        inst.addListener(
            self.family_sub,
            ntcore.EventFlags.kValueAll,
            lambda event: (
                setattr(
                    state.settings.apriltag3, "families", event.data.value.getString()
                ),
                setattr(state, "detector_update_needed", True),
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
            ),
        )
        inst.addListener(
            self.team_sub,
            ntcore.EventFlags.kValueAll,
            update_server_address,
        )

        # probably not needed
        # self.instance = inst

    # TODO: add timestamps, latency
    def update_data(self, timestamp: float):
        # Update fps
        self.fps_pub.set(state.fps)
        self.uptime_pub.set(int(state.frame_times[-1] - state.frame_times[0]))

    def periodic(self, timestamp: float):
        self.update_data(timestamp)
