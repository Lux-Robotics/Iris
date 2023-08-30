import apriltag
import util.constants as constants
from util.vision_types import TagObservation
import numpy as np

detector = apriltag.Detector(constants.detector_options)


def find_corners(image):
    # Detect AprilTags in the image
    detections = detector.detect(image)
    detections_filtered = []
    for detection in detections:
        margin = getattr(detection, 'decision_margin')
        if margin > 35:
            detections_filtered.append(detection)
    if len(detections) == 0:
        return []
    return [TagObservation(detection.tag_id, detection.corners.reshape((1, 4, 2)).astype(np.float32)) for detection in detections_filtered]