import math
import time

import cv2
import numpy as np

import util.config as config


def draw_detections(image, detections, scale):
    # Draw corners on the image
    for detection in detections:
        cv2.aruco.drawDetectedMarkers(image, np.array([detection.corners / scale]), np.array([[detection.tag_id]]))
    return image


def process():
    if not config.new_data or config.detections is None or config.last_frame is None:
        # Timeout so thread doesn't hog CPU
        time.sleep(0.005)
        return None, None, None

    frame, detections = config.last_frame, config.detections
    config.new_data = False

    scale = math.ceil(max(frame.shape[1] / config.stream_res[0], frame.shape[0] / config.stream_res[1]))
    frame = cv2.resize(frame, dsize=(int(frame.shape[1] / scale), int(frame.shape[0] / scale)))

    detections_array = np.array(
        [np.concatenate((detection.corners.reshape(4, 2) / scale, detection.corners[0, :1] / scale)) for detection in
         detections])
    detection_ids = ["ID: " + str(detection.tag_id) for detection in detections]

    # im = draw_detections(frame, detections, scale)
    im = frame

    if config.preview_fps:
        cv2.putText(im, "FPS: " + str(9 / (config.fps[-1] - config.fps[-10])), (7, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (100, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(im, "Frame: " + str(len(config.fps) - 9), (7, 80), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (100, 255, 0), 2,
                    cv2.LINE_AA)

    return im, detections_array, detection_ids
