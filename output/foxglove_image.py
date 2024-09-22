from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage
from foxglove_schemas_protobuf.ImageAnnotations_pb2 import ImageAnnotations
from mcap_protobuf.writer import Writer

import util.state as state
from output.float_message_pb2 import FloatMessage
from output.foxglove_utils import points, timestamp


def get_image(now: int, buffer: bytes) -> CompressedImage:
    # /camera/image
    return CompressedImage(
        timestamp=timestamp(now),
        frame_id="camera",
        format="jpeg",
        data=buffer,
    )


def get_frame(now: int, points_array, ids, ignored_points_array, ignored_ids) -> (
    ImageAnnotations,
    ImageAnnotations,
    FloatMessage,
):

    # /camera/annotations
    point, id = points(points_array, ids, now)
    ann = ImageAnnotations(points=point, texts=id)
    ignored_point, ignored_id = points(ignored_points_array, ignored_ids, now, bad=True)
    ignored_ann = ImageAnnotations(points=ignored_point, texts=ignored_id)
    return (
        ann,
        ignored_ann,
        FloatMessage(number=state.fps),
    )


def write_frame(
    now: int,
    buffer: bytes,
    points_array,
    ids,
    ignored_points_array,
    ignored_ids,
    writer: Writer,
    disk_full: bool = False,
) -> None:
    ann, ignored_ann, fps = get_frame(
        now, points_array, ids, ignored_points_array, ignored_ids
    )
    if not disk_full and buffer is not None:
        img = get_image(now, buffer)
        writer.write_message(
            topic="/camera/image",
            log_time=now,
            message=img,
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
        topic="/camera/fps", log_time=now, message=fps, publish_time=now
    )
