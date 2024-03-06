import math
import time

import cv2
import numpy as np

import util.config as config


def process(max_resolution, mode: str):
    current_time = time.time()
    if config.filtered_detections is None or config.last_frame is None:
        # Timeout so thread doesn't hog CPU
        time.sleep(0.005)
        return None, None, None, None, None

    if mode == "log":
        if not config.new_data or (
            current_time - config.robot_last_enabled > 5.0
            and current_time - config.last_logged_timestamp < 0.5
        ):
            time.sleep(0.005)
            return None, None, None, None, None
        else:
            config.last_logged_timestamp = current_time
            config.new_data = False

    frame, filtered_detections, ignored_detections = (
        config.last_frame,
        config.filtered_detections,
        config.ignored_detections,
    )

    scale = math.ceil(
        max(frame.shape[1] / max_resolution[0], frame.shape[0] / max_resolution[1])
    )
    frame = cv2.resize(
        frame, dsize=(int(frame.shape[1] / scale), int(frame.shape[0] / scale))
    )

    detections_array = np.array(
        [detection.corners.reshape(4, 2) / scale for detection in filtered_detections]
    )
    detection_ids = [
        "ID: " + str(detection.tag_id) for detection in filtered_detections
    ]

    ignored_detections_array = np.array(
        [detection.corners.reshape(4, 2) / scale for detection in ignored_detections]
    )
    ignored_detection_ids = [
        "ID: " + str(detection.tag_id) for detection in ignored_detections
    ]

    return (
        frame,
        detections_array,
        detection_ids,
        ignored_detections_array,
        ignored_detection_ids,
    )
