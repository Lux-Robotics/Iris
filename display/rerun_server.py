import rerun as rr

import util.config as config
import display.pipeline

rr.init("PeninsulaPerception", spawn=False)

rr.save("log.rrd")
# rr.connect()

def start():
    while True:
        frame, detections = display.pipeline.process()
        if frame is None:
            continue
        else:
            rr.set_time_sequence(config.device_id, len(config.fps) - 10)
            rr.log(config.device_id, rr.Image(frame))
            rr.log(config.device_id, rr.TimeSeriesScalar(9 / (config.fps[-1] - config.fps[-10]), label="fps"))
            rr.log(config.device_id, rr.LineStrips2D(detections))
