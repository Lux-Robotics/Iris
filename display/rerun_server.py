import rerun as rr
import cv2

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
            # Encode the frame in JPEG format
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.stream_quality]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            # Convert the frame to bytes
            frame_bytes = buffer.tobytes()
            rr.set_time_sequence(config.device_id, len(config.fps) - 10)
            rr.log(config.device_id, rr.ImageEncoded(contents=frame_bytes))
            rr.log(config.device_id, rr.TimeSeriesScalar(9 / (config.fps[-1] - config.fps[-10]), label="fps"))
            rr.log(config.device_id, rr.LineStrips2D(detections, labels=None))
