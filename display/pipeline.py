import cv2
import util.config as config
import numpy as np


def draw_detections(image, detections):
    # Draw corners on the image
    for detection in detections:
        cv2.aruco.drawDetectedMarkers(image, np.array([detection.corners]), np.array([[detection.tag_id]]))
    return image


def process():
    if config.detections is None or config.last_frame is None:
        return None

    im = draw_detections(config.last_frame, config.detections)

    if config.preview_fps:
        cv2.putText(im, "FPS: " + str(9 / (config.fps[-1] - config.fps[-10])), (7, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (100, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(im, "Frame: " + str(len(config.fps) - 9), (7, 80), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (100, 255, 0), 2,
                    cv2.LINE_AA)

    return im
