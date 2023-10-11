import rerun as rr
import cv2

import util.config as config
import display.pipeline
import datetime

import util.vision_types as vt

import numpy as np

import os

rr.init("PeninsulaPerception", spawn=False)

# Create logs director if doesn't exist
if not os.path.exists("logs/"):
    os.makedirs("logs/")

timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
rr.save("logs/log-" + timestamp + ".rrd")
# rr.connect()

def start():
    rr.log("world", rr.ViewCoordinates.FLU, timeless=True)

    for tag in config.tag_world_coords:
        rr.log("world/tag"+str(tag), rr.Points3D([[corner.translation().X(),corner.translation().Y(),corner.translation().Z()] for corner in config.tag_world_coords[tag].corners]), timeless=True)

    while True:
        frame, detections, ids = display.pipeline.process()
        if frame is None:
            continue
        else:
            # Encode frame
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.stream_quality]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            # Convert the frame to bytes
            frame_bytes = buffer.tobytes()
            rr.set_time_sequence("world/" + config.device_id, len(config.fps) - 10)
            rr.log("world/" + config.device_id, rr.ImageEncoded(contents=frame_bytes))
            rr.log("world/" + config.device_id, rr.TimeSeriesScalar(9 / (config.fps[-1] - config.fps[-10]), label="fps"))
            rr.log("world/" + config.device_id, rr.LineStrips2D(detections, labels=ids))
            rr.log("world/" + config.device_id, rr.Pinhole(focal_length=900, width=1600, height=1300))
            if(len(config.poses) > 0):
                a = config.poses[0]
                q = a.get_object_pose()
                quat = q.rotation().getQuaternion()
                trans = q.translation()
                rr.log("world/" + config.device_id, rr.Transform3D(translation=[trans.X(), trans.Y(), trans.Z()], rotation=rr.Quaternion(xyzw=np.array([quat.X(), quat.Y(), quat.Z(), quat.W()], dtype=np.float32)), from_parent=True)) # Not correct
