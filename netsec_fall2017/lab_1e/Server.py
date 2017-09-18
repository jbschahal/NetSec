import playground
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import STRING, BUFFER
from playground.network.common import StackingProtocol, StackingTransport, StackingProtocolFactory
from playground.asyncio_lib.testing import TestLoopEx
from asyncio import Protocol
import asyncio
import datetime
import sys

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
            if isinstance(pckt, RequestWriteMessage):
                print("Got Packet 1")
                print(pckt)
                print("Packet Details: ClientID: " + pckt.clientID +"\n")
                respondPacket = RequestReceiverInfo()
            elif isinstance(pckt, SendReceiverInfo):
                print("Got Packet 3")
                print(pckt)
                print("Packet Details: ReceiverID: " + pckt.receiverID)
                print("Message: " + str(pckt.message) +"\n")
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
            print(pckt)
            if isinstance(pckt, RequestReceiverInfo):
                print("Got packet 2")
                print(pckt)
                print("Packet Details: Only request was transfered for this packet\n")
                respondPacket = SendReceiverInfo()
                respondPacket.receiverID = self._receiver_id
                respondPacket.message = self._msg
            elif isinstance(pckt, MessageSent):
                print("Got Packet 4")
                print(pckt)
                print("Packet Details: MessageSentTime: " + pckt.messageSentTime + "\n")
                self.connection_lost()
                return

            self.transport.write(respondPacket.__serialize__())

    def start_communication(self, _id): ##Sending the first pacekt and setting the variable values
        self._receiver_id = "r_ID"
        self._msg = b'This is a test Message'
        initialPacket = RequestWriteMessage(clientID = _id)
        self.transport.write(initialPacket.__serialize__())
        
    def connection_lost(self, reason=None):
        print("Comminication Ended\n")



class PassthroughLayerOne(StackingProtocol):
    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print("Connection Mande to passthrough 1")
        self.higherProtocol().connection_made(StackingTransport(transport))

    def data_received(self, data):
        self.higherProtocol().data_received(data)


class PassthroughLayerTwo(StackingProtocol):
    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print("Connection Made to passthrough 2")
        self.higherProtocol().connection_made(StackingTransport(transport))

    def data_received(self, data):
        self.higherProtocol().data_received(data)


class ClientControl:
    def __init__(self):
        self.txProtocol = None
        
    def buildProtocol(self):
        return MessagingClientProtocol()
        
    def connect(self, txProtocol):
        self.txProtocol = txProtocol
        print("Connection to Server Established!")
        print("Enter clientID: ")
        
    def stdinAlert(self):
        data = sys.stdin.readline()
        if data and data[-1] == "\n":
            data = data[:-1] # strip off \n
        self.txProtocol.start_communication(data)



    
if __name__ == "__main__":

    f = StackingProtocolFactory(lambda: PassthroughLayerOne(), lambda: PassthroughLayerTwo())
    ptConnector = playground.Connector(protocolStack=f)
    playground.setConnector("passthrough", ptConnector)
    
    loop = asyncio.get_event_loop()
    coro = playground.getConnector("passthrough").create_playground_server(lambda: MessagingServerProtocol(), 8000)
    server = loop.run_until_complete(coro)
    print("Echo Server Started at {}".format(server.sockets[0].gethostname()))
    loop.run_forever()
    loop.close()

