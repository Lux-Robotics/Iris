from mcap_protobuf.writer import Writer

from foxglove_schemas_protobuf.CameraCalibration_pb2 import CameraCalibration
from foxglove_schemas_protobuf.ImageAnnotations_pb2 import ImageAnnotations
from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage
from output.float_message_pb2 import FloatMessage

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
    # cal = CameraCalibration(
    #     timestamp=timestamp(now),
    #     frame_id="camera",
    #     width=config.resx,
    #     height=config.resy,
    #     distortion_model="rational_polynomial",
    #     D=config.dist_coeffs,
    #     K=config.camera_matrix
    # )
    # writer.write_message(
    #     topic="/camera/calibration",
    #     log_time=now,
    #     message=cal,
    #     publish_time=now,
    # )

    # /camera/annotations
    point, id = points(points_array, ids, now)
    ann = ImageAnnotations(points=point, texts=id)
    writer.write_message(
        topic="/camera/annotations",
        log_time=now,
        message=ann,
        publish_time=now,
    )
    # /camera/fps
    writer.write_message(
        topic="/camera/fps",
        log_time=now,
        message=FloatMessage(number=9 / (config.fps[-1] - config.fps[-10])),
        publish_time=now
    )
