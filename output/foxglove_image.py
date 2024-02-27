from foxglove_schemas_protobuf.CameraCalibration_pb2 import CameraCalibration
from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage
from foxglove_schemas_protobuf.ImageAnnotations_pb2 import ImageAnnotations
from mcap_protobuf.writer import Writer

import util.config as config
from output.float_message_pb2 import FloatMessage
from output.foxglove_utils import timestamp, points


def get_frame(now: int, buffer: bytes, points_array, ids, ignored_points_array, ignored_ids) -> (
        CompressedImage, CameraCalibration, ImageAnnotations, ImageAnnotations, FloatMessage):
    # /camera/image
    img = CompressedImage(
        timestamp=timestamp(now),
        frame_id="camera",
        format="jpeg",
        data=buffer,
    )

    # /camera/calibration
    cal = CameraCalibration(
        timestamp=timestamp(now),
        frame_id="camera",
        width=config.resx,
        height=config.resy,
        distortion_model="rational_polynomial",
        D=config.dist_coeffs.tolist(),
        K=config.camera_matrix.reshape(9).tolist(),
        R=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
        P=[1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
    )

    # /camera/annotations
    point, id = points(points_array, ids, now)
    ann = ImageAnnotations(points=point, texts=id)
    ignored_point, ignored_id = points(ignored_points_array, ignored_ids, now, bad=True)
    ignored_ann = ImageAnnotations(points=ignored_point, texts=ignored_id)
    return img, cal, ann, ignored_ann, FloatMessage(number=9 / (config.fps[-1] - config.fps[-10]))


def write_frame(now: int, buffer: bytes, points_array, ids, ignored_points_array, ignored_ids, writer: Writer, disk_full: bool = False) -> None:
    img, cal, ann, ignored_ann, fps = get_frame(now, buffer, points_array, ids, ignored_points_array, ignored_ids)
    if not disk_full:
        writer.write_message(
            topic="/camera/image",
            log_time=now,
            message=img,
            publish_time=now,
        )
    writer.write_message(
        topic="/camera/calibration",
        log_time=now,
        message=cal,
        publish_time=now,
    )
    writer.write_message(
        topic="/camera/annotations",
        log_time=now,
        message=ann,
        publish_time=now,
    )
    writer.write_message(
        topic="/camera/ignored_annotations",
        log_time=now,
        message=ignored_ann,
        publish_time=now,
    )
    # /camera/fps
    writer.write_message(
        topic="/camera/fps",
        log_time=now,
        message=fps,
        publish_time=now
    )
