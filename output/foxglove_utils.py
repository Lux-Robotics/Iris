from google.protobuf import timestamp_pb2

from foxglove_schemas_protobuf.PointsAnnotation_pb2 import PointsAnnotation
from foxglove_schemas_protobuf.Color_pb2 import Color
from foxglove_schemas_protobuf.Point2_pb2 import Point2


def timestamp(time_ns: int) -> timestamp_pb2.Timestamp:
    return timestamp_pb2.Timestamp(seconds=time_ns // 1_000_000_000, nanos=time_ns % 1_000_000_000)


def points(point_array, now: int):
    points_out = []
    for series in point_array:
        points_out.append(
            PointsAnnotation(timestamp=timestamp(now), type="LINE_LOOP", points=[Point2(x=x, y=y) for x, y in series],
                             outline_color=Color(r=0, b=0, g=1, a=1), thickness=1))
    return points_out
