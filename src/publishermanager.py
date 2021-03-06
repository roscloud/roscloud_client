# Defines PublisherManager class.

import rospy
from rospy_message_converter import message_converter

# Manages ROS publishers for received messages.
class PublisherManager(object):

    def __init__(self, use_local_time):
        self.use_local_time = use_local_time
        self.pubs = dict()

    # Converts message dictionary to ROS message for publishing.
    def create_msg(self, msg_dict, msg_type):
        namespace, msg_name = msg_type.split("/")
        mod = __import__(namespace + ".msg")
        msg_cls = getattr(mod.msg, msg_name)
        msg = message_converter.convert_dictionary_to_ros_message(
            msg_type, msg_dict)
        if self.use_local_time:
            if hasattr(msg, "header"):
                msg.header.stamp = rospy.get_rostime()
            elif msg_type == "tf2_msgs/TFMessage":
                for t in msg.transforms:
                    t.header.stamp = rospy.get_rostime()
        return msg, msg_cls

    # Publishes newly received messages.
    # Creates new Publishers for new topics.
    def publish(self, data):
        msg, msg_cls = self.create_msg(data["Msg"], data["Type"])
        topic = data["Topic"]
        if not topic in self.pubs.keys():
            self.pubs[topic] = rospy.Publisher(topic, msg_cls, queue_size=1)
        self.pubs[topic].publish(msg)
