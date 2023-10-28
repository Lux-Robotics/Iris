from mcap_protobuf.writer import Writer

from foxglove_schemas_protobuf.Vector3_pb2 import Vector3
from foxglove_schemas_protobuf.Quaternion_pb2 import Quaternion
from foxglove_schemas_protobuf.Pose_pb2 import Pose
from foxglove_schemas_protobuf.FrameTransform_pb2 import FrameTransform
from foxglove_schemas_protobuf.SceneEntity_pb2 import SceneEntity
from foxglove_schemas_protobuf.SceneUpdate_pb2 import SceneUpdate
from foxglove_schemas_protobuf.ModelPrimitive_pb2 import ModelPrimitive
from foxglove_schemas_protobuf.Color_pb2 import Color
from google.protobuf.duration_pb2 import Duration

from util.vision_types import Pose as PerceptionPose
from output.foxglove_utils import timestamp


def write_pose(writer: Writer, now: int, pose: PerceptionPose):
    object_pose = pose.get_object_pose()
    position = Vector3(
        x=object_pose.translation().X(),
        y=object_pose.translation().Y(),
        z=object_pose.translation().Z()
    )
    orientation = Quaternion(
        w=object_pose.rotation().getQuaternion().W(),
        x=object_pose.rotation().getQuaternion().X(),
        y=object_pose.rotation().getQuaternion().Y(),
        z=object_pose.rotation().getQuaternion().Z(),
    )
    frame_reference = FrameTransform(
        timestamp=timestamp(now),
        parent_frame_id="base_link",
        child_frame_id="camera",
        translation=position,
        rotation=orientation
    )
    writer.write_message(
        topic="/camera/pose",
        log_time=now,
        message=frame_reference,
        publish_time=now,
    )


def setup_field(writer: Writer, now: int):
    with open("assets/2023_chargedup.glb", mode='rb') as f:  # b is important -> binary
        field_model = f.read()

    field = ModelPrimitive(
        pose=Pose(position=Vector3(x=8.270875, y=4.00685, z=0), orientation=Quaternion(w=0, x=0, y=0, z=1)),
        scale=Vector3(x=1, y=1, z=1),
        override_color=True,
        color=Color(r=1, g=1, b=1, a=0.3),
        data=field_model,
        media_type="model/gltf-binary"
    )
    entities = SceneEntity(
        timestamp=timestamp(now),
        lifetime=Duration(seconds=0),
        frame_id="base_link",
        models=[field]
    )
    update = SceneUpdate(entities=[entities])
    writer.write_message(
        topic="/world/field",
        log_time=now,
        message=update,
        publish_time=now
    )
