import subprocess

from ntcore import Event

import util.state
from util.state import logger, settings

device_path = "/dev/v4l-subdev2"


def change_ctrl(ctrl: str, value: int):
    try:
        subprocess.check_output(
            [
                "v4l2-ctl",
                "-d",
                device_path,
                "-c",
                f"{ctrl}={value}",
            ],
            stderr=subprocess.STDOUT,
        )
        util.state.save_settings()

    except Exception as e:
        logger.error(e)


def update_gain(event: Event):
    v = event.data.value.getInteger()
    settings.camera.gain = v
    change_ctrl("analogue_gain", v)


def update_exposure(event: Event):
    v = event.data.value.getInteger()
    settings.camera.exposure = v
    change_ctrl("exposure", v)


def update_brightness(event: Event):
    v = event.data.value.getInteger()
    settings.camera.brightness = v
    change_ctrl("brightness", v)
