from typing import List

import util.state as state
from util.vision_types import TagObservation


def filter_tags(
    detections: List[TagObservation],
) -> (List[TagObservation], List[TagObservation]):
    filtered_detections = []
    ignored_detections = []
    for detection in detections:
        if detection.tag_id not in state.tag_world_coords:
            continue

        if detection.tag_id in state.ignored_tags:
            ignored_detections.append(detection)

        else:
            filtered_detections.append(detection)

    return filtered_detections, ignored_detections
