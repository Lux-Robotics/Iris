import datetime
import os

import cv2
import numpy as np
import rerun as rr

import output.pipeline
import util.config as config

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
        rr.log("world/tag" + str(tag), rr.Points3D(
            [[corner.translation().X(), corner.translation().Y(), corner.translation().Z()] for corner in
             config.tag_world_coords[tag].corners]), timeless=True)

    while True:
        frame, detections, ids = output.pipeline.process()
        if frame is None:
            continue
        else:
            # Encode frame
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.stream_quality]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)

            # Convert the frame to bytes
            frame_bytes = buffer.tobytes()

            # Log fps
            rr.set_time_sequence("world/" + config.device_id, len(config.fps) - 10)
            rr.log("world/" + config.device_id,
                   rr.TimeSeriesScalar(9 / (config.fps[-1] - config.fps[-10]), label="fps"))

            # Log image
            rr.log("world/" + config.device_id, rr.ImageEncoded(contents=frame_bytes))

            # Log detections
            rr.log("world/" + config.device_id, rr.LineStrips2D(detections, labels=ids))

            # Log camera pose
            rr.log("world/" + config.device_id,
                   rr.Pinhole(image_from_camera=config.camera_matrix, width=config.resx, height=config.resy))

            if len(config.poses) > 0:
                camera_pose = config.poses[0].get_object_pose()
                pose_quaternion = camera_pose.rotation().getQuaternion()
                pose_translation = camera_pose.translation()

                rr.log("world/" + config.device_id,
                       rr.Transform3D(translation=[pose_translation.X(), pose_translation.Y(), pose_translation.Z()],
                                      rotation=rr.Quaternion(xyzw=np.array(
                                          [pose_quaternion.X(), pose_quaternion.Y(), pose_quaternion.Z(),
                                           pose_quaternion.W()], dtype=np.float32)), from_parent=True))
