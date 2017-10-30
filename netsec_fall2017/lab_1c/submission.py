from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import STRING, BUFFER
from playground.network.testing import mock
from playground.asyncio_lib.testing import TestLoopEx
from asyncio import Protocol
import asyncio
import datetime

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

class MessagingClientProtocol(Protocol):
    def __init__(self):
        transport = None
    
    def connection_made(self, transport):
        print("Client connected to server\n")
        self.transport = transport

    def data_received(self, data):                      ##Evaluating which packet is recieved and responding accordingly
        self._deserializer = PacketType.Deserializer()
        self._deserializer.update(data)
        for pckt in self._deserializer.nextPackets():
            print("Got a Packet from Server and the packet is ")
            print(pckt)
            if isinstance(pckt, RequestReceiverInfo):
                print("Got packet 2")
                print("Packet Details: Only request was transfered for this packet\n")
                respondPacket = SendReceiverInfo()
                respondPacket.receiverID = self._receiver_id
                respondPacket.message = self._msg
            elif isinstance(pckt, MessageSent):
                print("Got Packet 4")
                print("Packet Details: MessageSentTime: " + pckt.messageSentTime + "\n")
                self.connection_lost()
                return

            self.transport.write(respondPacket.__serialize__())

    def start_communication(self, client_id, receiver_id, msg): ##Sending the first pacekt and setting the variable values
        self._client_id = client_id
        self._receiver_id = receiver_id
        self._msg = msg
        initialPacket = RequestWriteMessage(clientID = self._client_id)
        self.transport.write(initialPacket.__serialize__())
        
    def connection_lost(self, reason=None):
        print("Comminication Ended\n")

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
                print("Packet Details: ClientID: " + pckt.clientID +"\n")
                respondPacket = RequestReceiverInfo()
            elif isinstance(pckt, SendReceiverInfo):
                print("Got Packet 3")
                print("Packet Details: ReceiverID: " + pckt.receiverID)
                print("Message: " + str(pckt.message) +"\n")
                respondPacket = MessageSent()
                respondPacket.messageSentTime = str(datetime.datetime.now())

            self.transport.write(respondPacket.__serialize__())

    def connection_lost(self, reason=None):
        print("Comminication Ended")

def BasicUnitTest():
    client = MessagingClientProtocol()
    server = MessagingServerProtocol()
    
    transportToServer = mock.MockTransportToProtocol(myProtocol=client)
    transportToClient = mock.MockTransportToProtocol(myProtocol=server)

    transportToServer.setRemoteTransport(transportToClient)
    transportToClient.setRemoteTransport(transportToServer)

    server.connection_made(transportToClient)
    client.connection_made(transportToServer)

    client.start_communication("jchahal1_S", "jchahal1_R", b'This is a test message')
   
#Main
if __name__ == "__main__":
    BasicUnitTest()
