import glob
import os
import shutil
import uuid
from typing import List

import cv2

import util.state as state


def take_snapshot(filename: str | None = None):
    """
    Takes a snapshot of the last captured frame and saves it as a PNG file.

    Args:
        filename (str): Optional. The name for the snapshot file. If not
                        provided, a UUID will be generated and used as the
                        filename.
    """
    if filename is None:
        filename = uuid.uuid4().hex

    if state.last_frame is not None:
        cv2.imwrite(
            os.path.join(state.snapshots_dir, str(filename) + ".png"), state.last_frame
        )
        state.nt_listener.snapshots_pub.set(list_snapshots())

    else:
        state.logger.info("Failed to take snapshot")


def clear_snapshots():
    if os.path.exists(state.snapshots_dir):
        shutil.rmtree(state.snapshots_dir)
    os.makedirs(state.snapshots_dir, exist_ok=True)
    state.nt_listener.snapshots_pub.set(list_snapshots())


def list_snapshots() -> List[str]:
    """Lists all snapshot files in the snapshots directory."""
    if not os.path.exists(state.snapshots_dir):
        return []
    return [
        os.path.basename(f)
        for f in glob.glob(os.path.join(state.snapshots_dir, "*.png"))
    ]


# TODO: add a hook from the main loop for video logging
