import time
import os
import datetime
import logging

from mcap_protobuf.writer import Writer

import output.pipeline
import cv2
import util.config as config

from output.foxglove_image import write_frame
from output.foxglove_pose import write_pose, setup_field
from output.foxglove_utils import timestamp
from foxglove_schemas_protobuf.Log_pb2 import Log


class FoxgloveLoggingHandler(logging.Handler):
    def __init__(self, writer: Writer):
        super().__init__()
        self.writer = writer

    @staticmethod
    def record_to_log(record: logging.LogRecord):
        return Log(
            timestamp=timestamp(int(record.created * 1e9)),
            level=record.levelname,
            message=record.getMessage()
        )

    def emit(self, record):
        try:
            now = time.time_ns()
            log_entry = self.record_to_log(record)

            # Send the log entry to Foxglove
            self.writer.write_message(
                topic="/log",
                log_time=now,
                message=log_entry,
                publish_time=now
            )
        except Exception as e:
            # Handle any errors that occur during logging
            self.handleError(record)


def main(log_dir: str):
    # Create logs director if doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    with open(log_dir + "log-" + timestamp + ".mcap", "wb") as f, Writer(f) as writer:
        start_time = time.time_ns()
        foxglove_handler = FoxgloveLoggingHandler(writer)
        foxglove_handler.setLevel(logging.DEBUG)
        config.logger.addHandler(foxglove_handler)
        setup_field(start_time, writer)
        config.logger.info(config.config_json)
        while True:
            now = time.time_ns()
            try:
                frame, points, ids = output.pipeline.process()
                if frame is None:
                    continue
                else:
                    # Encode the frame in JPEG format
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.log_quality]
                    ret, buffer = cv2.imencode('.jpg', frame, encode_param)
                    if not ret:
                        continue
            except Exception as e:
                config.logger.exception(e)

            # Convert the frame to bytes
            try:
                data = buffer.tobytes()
                write_frame(now, data, points, ids, writer)
                if len(config.poses) > 0:
                    write_pose(now, config.poses[0], "camera", writer)
                if len(config.poses) > 1:
                    write_pose(now, config.poses[1], "ambiguity", writer)
            except Exception as e:
                config.logger.exception(e)


def start(log_dir: str = "logs/"):
    main(log_dir)


if __name__ == "__main__":
    main("logs/")
