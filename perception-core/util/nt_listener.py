import ntcore

import util.config as config


class NTListener:
    def __init__(self):
        inst = ntcore.NetworkTableInstance.create()
        inst.startServer()

        self.fps_pub = inst.getDoubleTopic("fps").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True)
        )

        # camera settings
        self.brightness_sub = inst.getDoubleTopic("brightness").subscribe(0.0)
        self.exposure_sub = inst.getDoubleTopic("exposure").subscribe(0.0)
        self.gain_sub = inst.getDoubleTopic("gain").subscribe(0.0)

        # apriltag settings
        self.family_sub = inst.getStringTopic("tagFamily").subscribe(
            ""
        )  # 'tag16h5', 'tag25h9', 'tag36h11'
        self.family_pub = inst.getStringTopic("tagFamily").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True)
        )
        self.family_pub.set(config.settings.apriltag3.families)

        self.decimate_sub = inst.getDoubleTopic("decimate").subscribe(0.0)
        self.decimate_pub = inst.getDoubleTopic("decimate").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True)
        )
        self.decimate_pub.set(config.settings.apriltag3.quad_decimate)

        self.blur_sub = inst.getDoubleTopic("blur").subscribe(0.0)
        self.blur_pub = inst.getDoubleTopic("blur").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True)
        )
        self.blur_pub.set(config.settings.apriltag3.quad_sigma)

        self.n_threads_sub = inst.getIntegerTopic("threads").subscribe(0)
        self.n_threads_pub = inst.getIntegerTopic("threads").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True)
        )
        self.n_threads_pub.set(config.settings.apriltag3.threads)

        inst.addListener(
            self.family_sub,
            ntcore.EventFlags.kValueAll,
            lambda event: (
                setattr(
                    config.settings.apriltag3, "families", event.data.value.getString()
                ),
                setattr(config, "detector_update_needed", True),
            ),
        )
        inst.addListener(
            self.decimate_sub,
            ntcore.EventFlags.kValueAll,
            lambda event: (
                setattr(
                    config.settings.apriltag3,
                    "quad_decimate",
                    event.data.value.getDouble(),
                ),
                setattr(config, "detector_update_needed", True),
            ),
        )
        inst.addListener(
            self.blur_sub,
            ntcore.EventFlags.kValueAll,
            lambda event: (
                setattr(
                    config.settings.apriltag3,
                    "quad_sigma",
                    event.data.value.getDouble(),
                ),
                setattr(config, "detector_update_needed", True),
            ),
        )
        inst.addListener(
            self.n_threads_sub,
            ntcore.EventFlags.kValueAll,
            lambda event: (
                setattr(
                    config.settings.apriltag3, "threads", event.data.value.getInteger()
                ),
                setattr(config, "detector_update_needed", True),
            ),
        )

        # probably not needed
        # self.instance = inst

    # TODO: add timestamps, latency
    def update_data(self, timestamp: float):
        # Update fps
        try:
            fps = 9 / (config.fps[-1] - config.fps[-10])
        except:
            fps = 0
        self.fps_pub.set(fps)

    def periodic(self, timestamp: float):
        self.update_data(timestamp)
