import cv2

from util.config import settings
from util.vision_types import TagObservation

# Detect tags in the 16h5 family
# aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_16h5)
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)

detection_params = cv2.aruco.DetectorParameters()
detection_params.useAruco3Detection = settings.aruco.aruco3
detection_params.aprilTagQuadDecimate = settings.aruco.decimate

if settings.aruco.corner_refinement == "none":
    detection_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_NONE
elif settings.aruco.corner_refinement == "subpix":
    detection_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    detection_params.relativeCornerRefinmentWinSize = (
        settings.aruco.relative_refinement_window
    )
    detection_params.cornerRefinementWinSize = settings.aruco.max_refinement_window


def find_corners(image):
    detected_corners, ids, _ = cv2.aruco.detectMarkers(
        image, aruco_dict, parameters=detection_params
    )
    if len(detected_corners) == 0:
        return []
    return [
        TagObservation(tag_id[0], corners)
        for corners, tag_id in zip(detected_corners, ids)
    ]
