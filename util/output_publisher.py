import ntcore
import util.config as config
from util.vision_types import Pose
import math


class NTPublisher:
    # Initiate Connection
    def __init__(self, ip):
        ntcore.NetworkTableInstance.getDefault().setServer(ip)
        ntcore.NetworkTableInstance.getDefault().startClient4("Perception")
        self.output_table = ntcore.NetworkTableInstance.getDefault().getTable("/Perception/" + config.device_id + "/output")
        self.observations_pub = self.output_table.getDoubleArrayTopic("observations").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True))
        self.fps_pub = self.output_table.getDoubleTopic("fps").publish()

    def publish_data(self, pose: Pose, timestamp):
        observation_data = []
        if pose is not None:
            observation_data.append(pose.get_wpilib().translation().X())
            observation_data.append(pose.get_wpilib().translation().Y())
            observation_data.append(pose.get_wpilib().translation().Z())
            observation_data.append(pose.get_wpilib().rotation().getQuaternion().W())
            observation_data.append(pose.get_wpilib().rotation().getQuaternion().X())
            observation_data.append(pose.get_wpilib().rotation().getQuaternion().Y())
            observation_data.append(pose.get_wpilib().rotation().getQuaternion().Z())
        try:
            fps = 9 / (config.fps[-1] - config.fps[-10])
        except:
            fps = 0
        self.observations_pub.set(observation_data, math.floor(timestamp * 1000000))
        self.fps_pub.set(fps, math.floor(timestamp * 1000000))

