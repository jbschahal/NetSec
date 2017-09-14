from asyncio import Protocol
import asyncio
import playground
import sys
from Server import MessagingClientProtocol

    
if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(lambda: MessagingClientProtocol(), '127.0.0.1', port=8000)
    transport, protocol = loop.run_until_complete(coro)
    print("Echo Client Connected. Starting UI t:{}. p:{}".format(transport, protocol))
    _id = input("Enter id: ")
    protocol.start_communication(_id)
    loop.run_forever()
    loop.close()
