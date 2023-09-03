import cv2
import util.config as constants
import numpy as np


def draw_detections(image, detections):
    # Draw corners on the image
    for detection in detections:
        cv2.aruco.drawDetectedMarkers(image, np.array([detection.corners]), np.array([[detection.tag_id]]))
    return image


def process():
    if constants.detections is None or constants.last_frame is None:
        return None

    im = draw_detections(constants.last_frame, constants.detections)

    if constants.preview_fps:
        cv2.putText(im, "FPS: " + str(9 / (constants.fps[-1] - constants.fps[-10])), (7, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (100, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(im, "Frame: " + str(len(constants.fps) - 9), (7, 80), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (100, 255, 0), 2,
                    cv2.LINE_AA)

    if constants.preview_pose:
        try:
            pose_text = " y: " + str(constants.poses[3][1][0][0].round(2)) + " z: " + str(
                constants.poses[3][1][1][0].round(2)) + " x: " + str(constants.poses[3][1][2][0].round(2))
            cv2.putText(im, pose_text, (7, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 2, cv2.LINE_AA)
        except:
            pass

    return im
