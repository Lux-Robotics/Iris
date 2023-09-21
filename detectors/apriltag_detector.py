import apriltag
import util.config as config
from util.vision_types import TagObservation
import numpy as np

detector = apriltag.Detector(config.detector_options)


def find_corners(image):
    # Detect AprilTags in the image
    detections = detector.detect(image)
    detections_filtered = []
    for detection in detections:
        margin = getattr(detection, 'decision_margin')
        hamming = getattr(detection, 'hamming')
        if margin > 35 and hamming == 0:
            detections_filtered.append(detection)
    if len(detections) == 0:
        return []
    
    # change corner order to match aruco
    ordered_detections = np.vstack((detection.corners[2:], detection.corners[:2]))
    return [TagObservation(detection.tag_id, ordered_detections.reshape((1, 4, 2)).astype(np.float32)) for detection in detections_filtered]