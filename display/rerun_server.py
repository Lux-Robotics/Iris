import rerun as rr

import util.config as config
import display.pipeline

rr.init("PeninsulaPerception", spawn=False)

rr.save("log.rrd")

def start():
    while True:
        frame, detections = display.pipeline.process()
        if frame is None:
            continue
        else:
            rr.set_time_sequence(config.device_id, len(config.fps) - 10)
            rr.log_image(config.device_id, frame)
            rr.log_scalar(config.device_id, 9 / (config.fps[-1] - config.fps[-10]), label="fps")
            rr.log_line_strips_2d(config.device_id, detections)
