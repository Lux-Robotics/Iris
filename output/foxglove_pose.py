from mcap_protobuf.writer import Writer

from foxglove_schemas_protobuf.Vector3_pb2 import Vector3
from foxglove_schemas_protobuf.Quaternion_pb2 import Quaternion
from foxglove_schemas_protobuf.Pose_pb2 import Pose
from foxglove_schemas_protobuf.PoseInFrame_pb2 import PoseInFrame

from util.vision_types import Pose as PerceptionPose
from output.foxglove_utils import timestamp


def write_pose(writer: Writer, now: int, pose: PerceptionPose):
    object_pose = pose.get_object_pose()
    position = Vector3(
        x=object_pose.translation().X(),
        y=object_pose.translation().Y(),
        z=object_pose.translation().Z())
    orientation = Quaternion(
        w=object_pose.rotation().getQuaternion().W(),
        x=object_pose.rotation().getQuaternion().X(),
        y=object_pose.rotation().getQuaternion().Y(),
        z=object_pose.rotation().getQuaternion().Z(),
    )
    logged_pose = PoseInFrame(
        timestamp=timestamp(now),
        frame_id="camera",
        pose=Pose(
            position=position,
            orientation=orientation
        )
    )
    writer.write_message(
        topic="/camera/pose",
        log_time=now,
        message=logged_pose,
        publish_time=now,
    )
