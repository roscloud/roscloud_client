
import zlib
import json
import rospy
import time
import common
import struct
from std_msgs.msg import Float32
from autobahn.twisted.websocket import WebSocketServerProtocol


class MMServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        name = request.path[0:]
        common.add_client(name, self)
        self.name_of_client = name
        self.lat_pub = rospy.Publisher("/jammi/latency", Float32, queue_size=2)

    def onMessage(self, payload, is_binary):
        if is_binary:
            try:
                received_time = time.time()
                decompressed = zlib.decompress(payload)
                size = struct.unpack('=I', decompressed[:4])
                frmt = "%ds" % size[0]
                unpacked = struct.unpack('=I' + frmt, decompressed)
                msg = json.loads(unpacked[1])
                latency = Float32()
                latency.data = received_time - msg["stamp"]
                self.lat_pub.publish(latency)
                if msg["to"] == "*":
                    for name in common.clients.keys():
                        if name != msg["from"]:
                            common.get_client(name).sendMessage(payload, True)
                else:
                    recipients = msg["to"].split(' ')
                    for name in recipients:
                        common.get_client(name).sendMessage(payload, True)
            except KeyError:
                pass

    def onClose(self, was_clean, code, reason):
        common.remove_client(self.name_of_client)
