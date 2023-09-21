import math
import time

import cv2.gapi
import rerun as rr

import util.config as config
import display.pipeline

rr.init("PeninsulaPerception", spawn=True)


def start():
    while True:
        try:
            frame = display.pipeline.process()
            scale = math.ceil(max(frame.shape[1] / config.stream_res[0], frame.shape[0] / config.stream_res[1]))
            frame = cv2.resize(frame, dsize=(int(frame.shape[1] / scale), int(frame.shape[0] / scale)))
            if frame is None:
                continue
            else:
                rr.log_image("test_img", frame, jpeg_quality=30)
            time.sleep(0.02)
        except:
            time.sleep(0.02)
            continue
