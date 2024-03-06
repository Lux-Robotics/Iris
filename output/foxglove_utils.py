import asyncio
import signal
from typing import Any, Coroutine

from foxglove_schemas_protobuf.Color_pb2 import Color
from foxglove_schemas_protobuf.Point2_pb2 import Point2
from foxglove_schemas_protobuf.PointsAnnotation_pb2 import PointsAnnotation
from foxglove_schemas_protobuf.TextAnnotation_pb2 import TextAnnotation
from google.protobuf import timestamp_pb2


def timestamp(time_ns: int) -> timestamp_pb2.Timestamp:
    return timestamp_pb2.Timestamp(
        seconds=time_ns // 1_000_000_000, nanos=time_ns % 1_000_000_000
    )


def points(point_array, ids, now: int, bad=False):
    points_out = []
    labels_out = []
    if bad:
        color = Color(r=1, b=0, g=0, a=1)
    else:
        color = Color(r=0, b=0, g=1, a=1)
    for series, id in zip(point_array, ids):
        labels_out.append(
            TextAnnotation(
                timestamp=timestamp(now),
                position=Point2(x=series[3][0], y=series[3][1]),
                text=id,
                text_color=color,
                font_size=8,
            )
        )
        points_out.append(
            PointsAnnotation(
                timestamp=timestamp(now),
                type="LINE_LOOP",
                points=[Point2(x=x, y=y) for x, y in series],
                outline_color=color,
                thickness=1,
            )
        )
    return points_out, labels_out


def run_cancellable(coro: Coroutine[None, None, Any]):
    """
    Run a coroutine such that a ctrl-C interrupt will gracefully cancel its
    execution and give it a chance to clean up before returning.

    See also: https://www.roguelynn.com/words/asyncio-graceful-shutdowns/
    """
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    task = loop.create_task(coro)
    try:
        loop.add_signal_handler(signal.SIGINT, task.cancel)
    except NotImplementedError:
        # signal handlers are not available on Windows, KeyboardInterrupt will be raised instead
        pass
    except:
        pass

    try:
        try:
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            task.cancel()
            loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass
