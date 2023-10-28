# This example writes a single point cloud message.
import time
import os
import datetime

from mcap_protobuf.writer import Writer

import output.pipeline
import cv2
import util.config as config

from output.foxglove_image import write_frame
from output.foxglove_pose import write_pose


def main():
    # Create logs director if doesn't exist
    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    with open("logs/log-" + timestamp + ".mcap", "wb") as f, Writer(f) as writer:
        # start = time.time_ns()
        while True:
            now = time.time_ns()
            frame, points, ids = output.pipeline.process()
            if frame is None:
                continue
            else:
                # Encode the frame in JPEG format
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.stream_quality]
                ret, buffer = cv2.imencode('.jpg', frame, encode_param)
                if not ret:
                    continue

            # Convert the frame to bytes
            data = buffer.tobytes()
            write_frame(writer, now, data, points, ids)
            if len(config.poses) > 0:
                write_pose(writer, now, config.poses[0])


def start():
    main()


if __name__ == "__main__":
    main()
