from google.protobuf import timestamp_pb2

from foxglove_schemas_protobuf.PointsAnnotation_pb2 import PointsAnnotation
from foxglove_schemas_protobuf.TextAnnotation_pb2 import TextAnnotation
from foxglove_schemas_protobuf.Color_pb2 import Color
from foxglove_schemas_protobuf.Point2_pb2 import Point2


def timestamp(time_ns: int) -> timestamp_pb2.Timestamp:
    return timestamp_pb2.Timestamp(seconds=time_ns // 1_000_000_000, nanos=time_ns % 1_000_000_000)


def points(point_array, ids, now: int):
    points_out = []
    labels_out = []
    for series, id in zip(point_array, ids):
        labels_out.append(TextAnnotation(timestamp=timestamp(now), position=Point2(x=series[3][0], y=series[3][1]),
                                         text=id, text_color=Color(r=0, b=0, g=1, a=1), font_size=8))
        points_out.append(
            PointsAnnotation(timestamp=timestamp(now), type="LINE_LOOP", points=[Point2(x=x, y=y) for x, y in series],
                             outline_color=Color(r=0, b=0, g=1, a=1), thickness=1))
    return points_out, labels_out
