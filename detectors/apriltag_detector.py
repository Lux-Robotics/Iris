import pyapriltags
import numpy as np

import util.config as config
from util.vision_types import TagObservation

detector = pyapriltags.Detector(
    families="tag36h11",
    nthreads=config.apriltag_nthreads,
    quad_decimate=config.apriltag_quad_decimate,
    refine_edges=config.apriltag_refine_edges,
)


def find_corners(image):
    # Detect AprilTags in the image
    detections = detector.detect(image)
    if len(detections) == 0:
        return []

    # change corner order to match aruco
    result = []
    for detection in detections:
        ordered_corners = np.vstack((detection.corners[2:], detection.corners[:2]))[::-1]
        result.append(
            TagObservation(
                detection.tag_id,
                ordered_corners.reshape((1, 4, 2)).astype(np.float32),
            )
        )
    return result
