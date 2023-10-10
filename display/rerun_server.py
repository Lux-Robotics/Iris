import rerun as rr
import cv2

import util.config as config
import display.pipeline

import util.vision_types as vt

import numpy as np

rr.init("PeninsulaPerception", spawn=False)

rr.save("log.rrd")
# rr.connect()

def start():
    while True:
        frame, detections, ids = display.pipeline.process()
        if frame is None:
            continue
        else:

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.stream_quality]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            # Convert the frame to bytes
            frame_bytes = buffer.tobytes()
            rr.set_time_sequence("camera/image", len(config.fps) - 10)
            rr.log("camera/image", rr.ImageEncoded(contents=frame_bytes))
            rr.log("camera/image", rr.TimeSeriesScalar(9 / (config.fps[-1] - config.fps[-10]), label="fps"))
            rr.log("camera/image", rr.LineStrips2D(detections, labels=ids))
            rr.log("camera/image", rr.Pinhole(focal_length=900, width=1600, height=1300))
            rr.log("camera", rr.ViewCoordinates.RDF, timeless=True)
            tags3d = []
            label = []
            for i in range(1, 9):
                config.tag_world_coords[i].get_corners()
                a = [config.tag_world_coords[i].get_corners()[0],
                    config.tag_world_coords[i].get_corners()[1],
                    config.tag_world_coords[i].get_corners()[2],
                    config.tag_world_coords[i].get_corners()[3],
                    config.tag_world_coords[i].get_corners()[0]]
                tags3d.append(a)
                label.append("ID: " + str(i))
            rr.log("camera/tag"+str(i), rr.LineStrips3D(tags3d, labels = label), timeless=True)
            if(len(config.poses) > 0):
                a = vt.Pose(config.poses[0].tvec, config.poses[0].rvec, error = 0)
                q = a.get_wpilib()
                quat = q.rotation().getQuaternion()
                trans = q.translation()
                rr.log("camera/image", rr.Transform3D(translation=[trans.X(), trans.Y(), trans.Z()], rotation=rr.Quaternion(xyzw=np.array([quat.X(), quat.Y(), quat.Z(), quat.W()], dtype=np.float32)), from_parent=True))