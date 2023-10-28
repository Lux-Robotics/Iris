from mcap_protobuf.writer import Writer

from foxglove_schemas_protobuf.Vector3_pb2 import Vector3
from foxglove_schemas_protobuf.Quaternion_pb2 import Quaternion
from foxglove_schemas_protobuf.Pose_pb2 import Pose
from foxglove_schemas_protobuf.PoseInFrame_pb2 import PoseInFrame
from foxglove_schemas_protobuf.FrameTransform_pb2 import FrameTransform

from util.vision_types import Pose as PerceptionPose
from output.foxglove_utils import timestamp


def write_pose(writer: Writer, now: int, pose: PerceptionPose):
    object_pose = pose.get_wpilib()
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
