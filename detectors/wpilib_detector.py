import robotpy_apriltag as apriltag
import util.config as config
from util.vision_types import TagObservation
import numpy as np

detector_options = apriltag.AprilTagDetector.Config()
detector_options.quadDecimate = 1.0

detector = apriltag.AprilTagDetector()
detector.setConfig(detector_options)
detector.addFamily("tag16h5")


def find_corners(image):
    # Detect AprilTags in the image
    detections = detector.detect(image)
    detections_filtered = []
    for detection in detections:
        margin = detection.getDecisionMargin()
        hamming = detection.getHamming()
        if margin > 35 and hamming == 0:
            detections_filtered.append(detection)
    if len(detections_filtered) == 0:
        return []

    # change corner order to match aruco
    return [TagObservation(detection.getId(), convert_corners(detection)) for detection in
            detections_filtered]


def convert_corners(detection: apriltag.AprilTagDetection):
    p1 = detection.getCorner(1)
    p2 = detection.getCorner(0)
    p3 = detection.getCorner(3)
    p4 = detection.getCorner(2)
    return np.array([
        [p1.x, p1.y],
        [p2.x, p2.y],
        [p3.x, p3.y],
        [p4.x, p4.y],
    ]).reshape((1, 4, 2)).astype(np.float32)
