from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class TagObservation:
    tag_id: int
    corners: np.ndarray[np.float64]
