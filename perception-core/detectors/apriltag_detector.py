import numpy as np
import pyapriltags

import util.state as state
from util.vision_types import TagObservation


def find_corners(image):
    # Detect AprilTags in the image
    detections = state.detector.detect(image)
    if len(detections) == 0:
        return []

    # change corner order to match aruco
    result = []
    for detection in detections:
        ordered_corners = np.vstack((detection.corners[2:], detection.corners[:2]))[
            ::-1
        ]
        result.append(
            TagObservation(
                detection.tag_id,
                ordered_corners.reshape((1, 4, 2)).astype(np.float32),
            )
        )
    return result
