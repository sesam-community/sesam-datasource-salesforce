import asyncio
import time

from aiosfstream import SalesforceStreamingClient
global liste
liste = []
def start_stream():
    loop = asyncio.get_event_loop()
    ent = loop.run_until_complete(asyncio.gather(stream_events()))

    #liste.extend(upd)
    get_ent(ent)
    start_stream()



async def stream_events():

    client =  SalesforceStreamingClient(
    consumer_key="<consumer key>",
    consumer_secret="<consumer secret>",
    username="<username>",
    password="<password>",
    sandbox=True)


    await client.open()# subscribe to topics
    await client.subscribe("/topic/<Topic name>")

    message = await client.receive()

    return message


def get_ent(ent):
    liste.extend(ent)
    print(liste)


if __name__ == "__main__":
    start_stream()
