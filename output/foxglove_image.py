from mcap_protobuf.writer import Writer

from io import BytesIO
from random import random
from typing import List
import struct

from foxglove_schemas_protobuf.CameraCalibration_pb2 import CameraCalibration
from foxglove_schemas_protobuf.CircleAnnotation_pb2 import CircleAnnotation
from foxglove_schemas_protobuf.PointsAnnotation_pb2 import PointsAnnotation
from foxglove_schemas_protobuf.Color_pb2 import Color
from foxglove_schemas_protobuf.ImageAnnotations_pb2 import ImageAnnotations
from foxglove_schemas_protobuf.Point2_pb2 import Point2
from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage
import util.config as config

from output.foxglove_utils import timestamp, points


def write_frame(writer: Writer, now: int, buffer: bytes, points_array, ids):
    # /camera/image
    img = CompressedImage(
        timestamp=timestamp(now),
        frame_id="camera",
        format="jpeg",
        data=buffer,
    )
    writer.write_message(
        topic="/camera/image",
        log_time=now,
        message=img,
        publish_time=now,
    )

    # /camera/calibration
    cal = CameraCalibration(
        timestamp=timestamp(now),
        frame_id="camera",
        width=config.resx,
        height=config.resy,
        distortion_model="plumb_bob",
        D=config.dist_coeffs,
        K=config.camera_matrix,
    )
    writer.write_message(
        topic="/camera/calibration",
        log_time=now,
        message=cal,
        publish_time=now,
    )
    # /camera/annotations
    point, id = points(points_array, ids, now)
    ann = ImageAnnotations(points=point, texts=id)
    writer.write_message(
        topic="/camera/annotations",
        log_time=now,
        message=ann,
        publish_time=now,
    )
