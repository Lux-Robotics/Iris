import math
import time

import cv2
import numpy as np

import util.state as state


def process_image(max_resolution):
    current_time = time.time()
    if state.filtered_detections is None or state.last_frame is None:
        # Timeout so thread doesn't hog CPU
        time.sleep(0.005)
        return None

    frame = state.last_frame

    scale = math.ceil(
        max(frame.shape[1] / max_resolution[0], frame.shape[0] / max_resolution[1])
    )
    frame = cv2.resize(
        frame, dsize=(int(frame.shape[1] / scale), int(frame.shape[0] / scale))
    )

    for detection in state.filtered_detections:
        cv2.aruco.drawDetectedMarkers(
            frame, np.array([detection.corners / scale]), np.array([[detection.tag_id]])
        )

    return frame, scale


def process_detections(scale):
    current_time = time.time()
    if state.filtered_detections is None or state.last_frame is None:
        # Timeout so thread doesn't hog CPU
        time.sleep(0.005)
        return None, None, None, None

    filtered_detections, ignored_detections = (
        state.filtered_detections,
        state.ignored_detections,
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
