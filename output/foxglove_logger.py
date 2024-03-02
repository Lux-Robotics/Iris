import datetime
import logging
import os
import shutil
import time

import cv2
from foxglove_schemas_protobuf.Log_pb2 import Log
from mcap_protobuf.writer import Writer

import output.pipeline
import util.config as config
from output.foxglove_image import write_frame
from output.foxglove_pose import write_pose, setup_field
from output.foxglove_utils import timestamp


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

def generate_filename(directory, prefix, extension='.mcap'):
    """Generate an incremental filename in the given directory."""
    i = 1
    while True:
        # Generate the next filename
        next_filename = f"{prefix}{i}{extension}"
        full_path = os.path.join(directory, next_filename)
        
        # Check if it exists
        if not os.path.exists(full_path):
            # If it doesn't exist, we've found our new filename
            return next_filename
        i += 1

def main(log_dir: str):
    # Create logs director if doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_name = generate_filename(log_dir, "log-" + config.device_id + "-")

    with open(os.path.join(log_dir, log_name), "wb") as f, Writer(f) as writer:

        # check if disk is too full 
        _, _, free_bytes = shutil.disk_usage(log_dir)
        safety_margin = 1 * 1024 * 1024 * 1024  # 1GB

        start_time = time.time_ns()
        foxglove_handler = FoxgloveLoggingHandler(writer)
        foxglove_handler.setLevel(logging.DEBUG)
        config.logger.addHandler(foxglove_handler)
        setup_field(start_time, writer)
        config.logger.info(config.config_json)
        if free_bytes < safety_margin:
            config.logger.error("Disk too full, video logging disabled")

        while True:
            now = time.time_ns()
            try:
                frame, points, ids, ignored_points, ignored_ids = output.pipeline.process(config.log_res, "log")
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
                write_frame(now, data, points, ids, ignored_points, ignored_ids, writer, free_bytes < safety_margin)
                if len(config.poses) > 0:
                    write_pose(now, config.poses[0], "camera", writer)
                if len(config.poses) > 1:
                    write_pose(now, config.poses[1], "ambiguity", writer)
            except Exception as e:
                config.logger.exception(e)


def start(log_dir: str = "logs/"):
    main(log_dir)


if __name__ == "__main__":
    main("logs")
