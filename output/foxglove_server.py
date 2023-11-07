import time
import os
from base64 import b64encode

import cv2

from typing import Set, Type

from foxglove_schemas_protobuf.CameraCalibration_pb2 import CameraCalibration
from foxglove_schemas_protobuf.ImageAnnotations_pb2 import ImageAnnotations
from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage
from foxglove_schemas_protobuf.FrameTransform_pb2 import FrameTransform
from foxglove_schemas_protobuf.SceneUpdate_pb2 import SceneUpdate
from output.float_message_pb2 import FloatMessage
from output.foxglove_pose import write_pose, setup_field
from output.foxglove_image import write_frame
import util.config as config
import output.pipeline

from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.descriptor import FileDescriptor
import google.protobuf.message
import asyncio

from output.foxglove_utils import run_cancellable
from foxglove_websocket.server import FoxgloveServer, FoxgloveServerListener
from foxglove_websocket.types import ChannelId


def build_file_descriptor_set(
        message_class: Type[google.protobuf.message.Message],
) -> FileDescriptorSet:
    """
    Build a FileDescriptorSet representing the message class and its dependencies.
    """
    file_descriptor_set = FileDescriptorSet()
    seen_dependencies: Set[str] = set()

    def append_file_descriptor(file_descriptor: FileDescriptor):
        for dep in file_descriptor.dependencies:
            if dep.name not in seen_dependencies:
                seen_dependencies.add(dep.name)
                append_file_descriptor(dep)
        file_descriptor.CopyToProto(file_descriptor_set.file.add())  # type: ignore

    append_file_descriptor(message_class.DESCRIPTOR.file)
    return file_descriptor_set


reset = False


async def main():
    global reset

    class Listener(FoxgloveServerListener):
        async def on_subscribe(self, server: FoxgloveServer, channel_id: ChannelId):
            global reset
            print("First client subscribed to", channel_id)
            if str(channel_id) == "6":
                reset = True

        async def on_unsubscribe(self, server: FoxgloveServer, channel_id: ChannelId):
            print("Last client unsubscribed from", channel_id)

    async with FoxgloveServer("0.0.0.0", 8765, "example server") as server:
        server.set_listener(Listener())
        ambiguity_pose_pub = await server.add_channel(
            {
                "topic": "/ambiguity/pose",
                "encoding": "protobuf",
                "schemaName": FrameTransform.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(FrameTransform).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )
        pose_pub = await server.add_channel(
            {
                "topic": "/camera/pose",
                "encoding": "protobuf",
                "schemaName": FrameTransform.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(FrameTransform).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )
        annotations_pub = await server.add_channel(
            {
                "topic": "/camera/annotations",
                "encoding": "protobuf",
                "schemaName": ImageAnnotations.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(ImageAnnotations).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )
        calibration_pub = await server.add_channel(
            {
                "topic": "/camera/calibration",
                "encoding": "protobuf",
                "schemaName": CameraCalibration.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(CameraCalibration).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )
        fps_pub = await server.add_channel(
            {
                "topic": "/camera/fps",
                "encoding": "protobuf",
                "schemaName": FloatMessage.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(FloatMessage).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )
        image_pub = await server.add_channel(
            {
                "topic": "/camera/image",
                "encoding": "protobuf",
                "schemaName": CompressedImage.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(CompressedImage).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )
        field_pub = await server.add_channel(
            {
                "topic": "/world/field",
                "encoding": "protobuf",
                "schemaName": SceneUpdate.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(SceneUpdate).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )

        while True:
            await asyncio.sleep(0.05)
            now = time.time_ns()

            frame, points, ids = output.pipeline.process(force_new_data=False)
            if frame is None:
                continue
            else:
                # Encode the frame in JPEG format
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.stream_quality]
                ret, buffer = cv2.imencode('.jpg', frame, encode_param)
                if not ret:
                    continue

            # Convert the frame to bytes
            data = buffer.tobytes()
            img, cal, ann, fps = write_frame(now, data, points, ids)
            if len(config.poses) > 0:
                pose = write_pose(now, config.poses[0], "camera")
                await server.send_message(pose_pub, now, pose.SerializeToString())
            if len(config.poses) > 1:
                ambiguity = write_pose(now, config.poses[1], "ambiguity")
                await server.send_message(ambiguity_pose_pub, now, ambiguity.SerializeToString())

            if reset:
                await server.send_message(field_pub, now, setup_field(now).SerializeToString())
                reset = False
            await server.send_message(image_pub, now, img.SerializeToString())
            await server.send_message(calibration_pub, now, cal.SerializeToString())
            await server.send_message(annotations_pub, now, ann.SerializeToString())
            await server.send_message(fps_pub, now, fps.SerializeToString())


def start():
    run_cancellable(main())


if __name__ == "__main__":
    run_cancellable(main())
