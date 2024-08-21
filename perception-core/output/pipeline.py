import math
import time

import cv2
import numpy as np

import util.config as config


def process_image(max_resolution):
    current_time = time.time()
    if config.filtered_detections is None or config.last_frame is None:
        # Timeout so thread doesn't hog CPU
        time.sleep(0.005)
        return None

    frame = config.last_frame

    # cv2.aruco.drawDetectedMarkers(frame, config.filtered_detections)

    scale = math.ceil(
        max(frame.shape[1] / max_resolution[0], frame.shape[0] / max_resolution[1])
    )
    frame = cv2.resize(
        frame, dsize=(int(frame.shape[1] / scale), int(frame.shape[0] / scale))
    )

    return frame, scale


def process_detections(scale):
    current_time = time.time()
    if config.filtered_detections is None or config.last_frame is None:
        # Timeout so thread doesn't hog CPU
        time.sleep(0.005)
        return None, None, None, None

    filtered_detections, ignored_detections = (
        config.filtered_detections,
        config.ignored_detections,
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
        detections_array,
        detection_ids,
        ignored_detections_array,
        ignored_detection_ids,
    )
