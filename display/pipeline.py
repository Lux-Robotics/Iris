import cv2
import util.config as config
import numpy as np
import math


def draw_detections(image, detections, scale):
    # Draw corners on the image
    for detection in detections:
        cv2.aruco.drawDetectedMarkers(image, np.array([detection.corners / scale]), np.array([[detection.tag_id]]))
    return image


def process():
    if config.detections is None or config.last_frame is None:
        return None

    frame = config.last_frame

    scale = math.ceil(max(frame.shape[1] / config.stream_res[0], frame.shape[0] / config.stream_res[1]))
    frame = cv2.resize(frame, dsize=(int(frame.shape[1] / scale), int(frame.shape[0] / scale)))

    im = draw_detections(frame, config.detections, scale)

    if config.preview_fps:
        cv2.putText(im, "FPS: " + str(9 / (config.fps[-1] - config.fps[-10])), (7, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (100, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(im, "Frame: " + str(len(config.fps) - 9), (7, 80), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (100, 255, 0), 2,
                    cv2.LINE_AA)

    return im
