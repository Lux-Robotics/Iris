import math
import time

import cv2
import numpy as np

import util.config as config


def process(max_resolution, force_new_data=True):
    if (force_new_data and not config.new_data) or config.detections is None or config.last_frame is None:
        # Timeout so thread doesn't hog CPU
        time.sleep(0.005)
        return None, None, None

    frame, detections = config.last_frame, config.detections
    config.new_data = not force_new_data

    scale = math.ceil(max(frame.shape[1] / max_resolution[0], frame.shape[0] / max_resolution[1]))
    frame = cv2.resize(frame, dsize=(int(frame.shape[1] / scale), int(frame.shape[0] / scale)))

    detections_array = np.array([detection.corners.reshape(4, 2) / scale for detection in detections])
    detection_ids = ["ID: " + str(detection.tag_id) for detection in detections]

    return frame, detections_array, detection_ids
