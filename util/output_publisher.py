import ntcore
import util.config as config
from util.vision_types import Pose
import math


class NTPublisher:
    # Initiate Connection
    def __init__(self, ip):
        ntcore.NetworkTableInstance.getDefault().setServer(ip)
        ntcore.NetworkTableInstance.getDefault().startClient4("Perception")
        self.output_table = ntcore.NetworkTableInstance.getDefault().getTable(
            "/Perception/" + config.device_id)
        self.observations_pub = self.output_table.getDoubleArrayTopic("observations").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True))
        self.observations2_pub = self.output_table.getDoubleArrayTopic("observations2").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True))
        self.fps_pub = self.output_table.getDoubleTopic("fps").publish()

    def publish_data(self, pose: Pose, tag, timestamp):
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
        observation_data_2 = []
        if tag is not None:
            observation_data_2.append(tag.get_wpilib().translation().X())
            observation_data_2.append(tag.get_wpilib().translation().Y())
            observation_data_2.append(tag.get_wpilib().translation().Z())
            observation_data_2.append(tag.get_wpilib().rotation().getQuaternion().W())
            observation_data_2.append(tag.get_wpilib().rotation().getQuaternion().X())
            observation_data_2.append(tag.get_wpilib().rotation().getQuaternion().Y())
            observation_data_2.append(tag.get_wpilib().rotation().getQuaternion().Z())

        self.observations_pub.set(observation_data, math.floor(timestamp * 1000000))
        self.observations2_pub.set(observation_data_2, math.floor(timestamp * 1000000))
        self.fps_pub.set(fps, math.floor(timestamp * 1000000))
