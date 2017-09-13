from asyncio import Protocol
import asyncio
import playground
import sys
from Server import MessagingClientProtocol

    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    coro = playground.getConnector().create_playground_connection(lambda: MessagingClientProtocol(), '20174.1.1.1', 8000)
    transport, protocol = loop.run_until_complete(coro)
    protocol.start_communication()
    loop.run_forever()
    loop.close()
