import rerun as rr

import util.config as config
import display.pipeline

import numpy as np

rr.init("PeninsulaPerception", spawn=False)

rr.save("log.rrd")
# rr.connect()

def start():
    while True:
        frame, detections = display.pipeline.process()
        if frame is None:
            continue
        else:
            rr.set_time_sequence("camera/image", len(config.fps) - 10)
            rr.log("camera/image", rr.Image(frame))
            rr.log("camera/image", rr.TimeSeriesScalar(9 / (config.fps[-1] - config.fps[-10]), label="fps"))
            rr.log("camera/image", rr.LineStrips2D(detections))
            rr.log("camera/image", rr.Pinhole(focal_length=900, width=1600, height=1300))
            rr.log("camera", rr.ViewCoordinates.RDF, timeless=True)
            for i in range(1, 9):
                rr.log("camera/tag"+str(i), rr.Points3D(config.tag_world_coords[i].get_corners()), timeless=True)
            if(len(config.poses) > 0):
                rr.log("camera/image", rr.Transform3D(translation=[config.poses[0].tvec[0][0], config.poses[0].tvec[1][0], config.poses[0].tvec[2][0]], rotation=rr.Quaternion(xyzw=np.array([0, 0, 0, 1], dtype=np.float32)), from_parent=True))

