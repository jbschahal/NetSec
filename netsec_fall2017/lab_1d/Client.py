from asyncio import Protocol
import asyncio
import playground
import sys
from Server import MessagingClientProtocol, ClientControl

    
if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    control = ClientControl()
    coro = playground.getConnector().create_playground_connection(control.buildProtocol, '20174.1.1.1', 8000)
    transport, protocol = loop.run_until_complete(coro)
    print("Echo Client Connected. Starting UI t:{}. p:{}".format(transport, protocol))
    loop.add_reader(sys.stdin, control.stdinAlert)
    control.connect(protocol)
    loop.run_forever()
    loop.close()
