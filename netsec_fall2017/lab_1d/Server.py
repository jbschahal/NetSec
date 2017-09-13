from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import STRING, BUFFER
from playground.network.testing import mock
from playground.asyncio_lib.testing import TestLoopEx
from asyncio import Protocol
import asyncio
import datetime
import playground

class RequestWriteMessage(PacketType):                  ##Packet1: Client requesting the server to send the message
    DEFINITION_IDENTIFIER = "lab1.packet1"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("clientID", STRING)
        ]

class RequestReceiverInfo(PacketType):                  ##Packet2: Server requesting the client to send the info for the messaeg
    DEFINITION_IDENTIFIER = "lab1.packet2"
    DEFINITION_VERSION = "1.0"

    
class SendReceiverInfo(PacketType):                     ##Packet3: Client sending the receiver's ID and the message to the server
    DEFINITION_IDENTIFIER = "lab1.packet3"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("receiverID", STRING),
        ("message", BUFFER)
        ]

class MessageSent(PacketType):                          ##Server sending the acknowledgment of sending the message along with the time of delivery
    DEFINITION_IDENTIFIER = "lab1.packet4"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("messageSentTime", STRING)
        ]

class MessagingServerProtocol (Protocol):
    def __init__(self):
        self.transport = None
    
    def connection_made(self, transport):
        print("\nServer connected to client\n")
        self.transport = transport

    def data_received(self, data):
        self._deserializer = PacketType.Deserializer()
        self._deserializer.update(data)
        for pckt in self._deserializer.nextPackets():
            print("Got a Packet from Client and the packet is ")
            print(pckt)
            if isinstance(pckt, RequestWriteMessage):
                print("Got Packet 1")
                respondPacket = RequestReceiverInfo()
            elif isinstance(pckt, SendReceiverInfo):
                print("Got Packet 3")
                respondPacket = MessageSent()
                respondPacket.messageSentTime = str(datetime.datetime.now())

            self.transport.write(respondPacket.__serialize__())

    def connection_lost(self, reason=None):
        print("Comminication Ended")

class MessagingClientProtocol(Protocol):
    def __init__(self):
        transport = None
    
    def connection_made(self, transport):
        print("Client connected to server\n")
        self.transport = transport

    def data_received(self, data):      ##Evaluating which packet is recieved and responding accordingly
        self._deserializer = PacketType.Deserializer()
        self._deserializer.update(data)
        for pckt in self._deserializer.nextPackets():
            print("Got a Packet from Server and the packet is ")
            print(pckt)
            if isinstance(pckt, RequestReceiverInfo):
                print("Got packet 2")
                respondPacket = SendReceiverInfo()
                respondPacket.receiverID = self._receiver_id
                respondPacket.message = self._msg
            elif isinstance(pckt, MessageSent):
                print("Got Packet 4")
                self.connection_lost()
                return

            self.transport.write(respondPacket.__serialize__())

    def start_communication(self, _id): ##Sending the first pacekt and setting the variable values
        self._receiver_id = "jchahal1_R"
        self._msg = b'This is a test Message'
        initialPacket = RequestWriteMessage(clientID = _id)
        self.transport.write(initialPacket.__serialize__())
        
    def connection_lost(self, reason=None):
        print("Comminication Ended\n")
    
if __name__ == "__main__":
    
    loop = asyncio.get_event_loop()
    coro = playground.getConnector().create_playground_server(lambda: MessagingServerProtocol(), 8000)
    server = loop.run_until_complete(coro)
    print("Echo Server Started at {}".format(server.sockets[0].gethostname()))
    loop.run_forever()
    loop.close()
