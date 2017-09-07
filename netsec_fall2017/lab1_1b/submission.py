from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import STRING, BUFFER

class RequestWriteMessage(PacketType):                  ##Packet1: Client requesting the server to send the message
    DEFINITION_IDENTIFIER = "jchaha1_lab2b1.packet"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("clientID", STRING)
        ]

packet1 = RequestWriteMessage()
packet1.clientID = "jchahal_s"                          ##Initializing the fields
packet1Bytes = packet1.__serialize__()                  ##Serialized packet bytes
packet1_dslzd = RequestWriteMessage.Deserialize(packet1Bytes)


class RequestReceiverInfo(PacketType):                  ##Packet2: Server requesting the client to send the info for the messaeg
    DEFINITION_IDENTIFIER = "jchaha1_lab2b2.packet"
    DEFINITION_VERSION = "1.0"

    FIELD = []

packet2 = RequestReceiverInfo()
packet2Bytes = packet2.__serialize__()
packet2_dslzd = RequestReceiverInfo.Deserialize(packet2Bytes)
    
class SendReceiverInfo(PacketType):                     ##Packet3: Client sending the receiver's ID and the message to the server
    DEFINITION_IDENTIFIER = "jchaha1_lab2b3.packet"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("receiverID", STRING),
        ("message", BUFFER)
        ]

packet3 = SendReceiverInfo()
packet3.receiverID = "jchahal_r"
packet3.message = b"Test Message."
packet3Bytes = packet3.__serialize__()
packet3_dslzd = SendReceiverInfo.Deserialize(packet3Bytes)


class MessageSent(PacketType):                          ##Server sending the acknowledgment of sending the message along with the time of delivery
    DEFINITION_IDENTIFIER = "jchaha1_lab2b4.packet"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("messageSentTime", STRING)
        ]
    
packet4 = MessageSent()
packet4.messageSentTime = "current Time"
packet4Bytes = packet4.__serialize__()
print(packet4Bytes)
packet4_dslzd = MessageSent.Deserialize(packet4Bytes)

def basicUnitTest():

    print("\n \nTest Starting \n")

    print("Packet1 Bytes:")
    print(packet1Bytes)
    print("Deserialized Packet1:")
    print(packet1_dslzd)
    print("packetLength:")
    print(len(packet1Bytes))
    assert packet1 == packet1_dslzd                     ##Testing the equality of the packet
    assert packet1.clientID == packet1_dslzd.clientID   ##Testing the equality of the values of the fields
    print("Assertion complete")
    
    print("\nPacket2 Bytes:")
    print(packet2Bytes)
    print("Deserialized Packet2")
    print(packet2_dslzd)
    print("packetLength:")
    print(len(packet2Bytes))
    assert packet2 == packet2_dslzd
    print("Assertion complete")

    print("\nPacket3 Bytes:")
    print(packet3Bytes)
    print("Deserialized Packet3")
    print(packet3_dslzd.message)
    print("packetLength:")
    print(len(packet3Bytes))
    assert packet3 == packet3_dslzd
    assert packet3_dslzd.receiverID == "jchahal_r"
    assert packet3_dslzd.message == b"Test Message."
    print("Assertion complete")

    print("\nPacket4 Bytes:")
    print(packet4Bytes)
    print("Deserialized Packet4 \n")
    print(packet4_dslzd)
    print("packetLength:")
    print(len(packet4Bytes))
    assert packet4 == packet4_dslzd
    assert packet4.messageSentTime == packet4_dslzd.messageSentTime
    print("Assertion complete")

    print("\nChecking the equality of different packets: packet1 and packet3 after deserializing")
    if packet1_dslzd == packet3_dslzd:                  ##Testing the equality of two different packets
        print("They are equal")
    else:
        print("They are not equal")

    packetBytes = packet1Bytes + packet2Bytes + packet3Bytes + packet4Bytes
    print("\nTotal packetBytes")
    print(packetBytes)
    print("\nTotal length:")
    print(len(packetBytes))

    print("\n")

    deserializer = PacketType.Deserializer()            ##Deserializing the packets chunck by chunck and keeping a note when a whole packet has been deserialized
    print("Starting with {} byets of data".format(len(packetBytes)))
    while len(packetBytes)>0:
        chunk, packetBytes = packetBytes[:10], packetBytes[10:]
        deserializer.update(chunk)
        print("Another 10 bytes loaded into deserializer, Left = {}".format(len(packetBytes)))
        for packet in deserializer.nextPackets():
            print("got a packet!")
            if packet == packet1: print("It's packet 1")
            elif packet == packet2: print("It's packet 2")
            elif packet == packet3: print("It's packet 3")
            elif packet == packet4: print("It's packet 4")

if __name__=="__main__":
    basicUnitTest()
