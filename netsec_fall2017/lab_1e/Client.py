from asyncio import Protocol
import asyncio
import playground
import sys
from Server import ClientControl, PassthroughLayerOne, PassthroughLayerTwo
from playground.network.common import StackingProtocol, StackingTransport, StackingProtocolFactory

    
if __name__ == "__main__":


    f = StackingProtocolFactory(lambda: PassthroughLayerOne(), lambda: PassthroughLayerTwo())
    ptConnector = playground.Connector(protocolStack=f)
    playground.setConnector("passthrough", ptConnector)

    loop = asyncio.get_event_loop()
    control = ClientControl()
    coro = playground.getConnector("passthrough").create_playground_connection(control.buildProtocol, '20174.1.1.1', 8000)
    transport, protocol = loop.run_until_complete(coro)
    print("Echo Client Connected. Starting UI t:{}. p:{}".format(transport, protocol))
    loop.add_reader(sys.stdin, control.stdinAlert)
    control.connect(protocol)
    loop.run_forever()
    loop.close()
