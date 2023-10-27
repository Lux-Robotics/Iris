# This example writes a single point cloud message.
import sys
import time

from mcap_protobuf.writer import Writer

import output.pipeline
import cv2
import util.config as config

from output.foxglove_image import write_frame


def main():
    with open("out.mcap", "wb") as f, Writer(f) as writer:
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
            write_frame(writer, now, data, points)


def start():
    main()


if __name__ == "__main__":
    main()
