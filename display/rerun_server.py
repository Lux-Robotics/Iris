import rerun as rr

import util.config as config
import display.pipeline

rr.init("PeninsulaPerception", spawn=False)

rr.save("log.rrd")

def start():
    while True:
        frame = display.pipeline.process()
        if frame is None:
            continue
        else:
            rr.log_image("stream", frame, jpeg_quality=config.stream_quality)
