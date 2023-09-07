import json
import asyncio

from django.conf import settings
from asgiref.sync import async_to_sync

from pyensign.events import Event
from pyensign.ensign import Ensign


INSTANCES = settings.ENSIGN["INSTANCES_TOPIC"]

@async_to_sync
async def connect():
    client = Ensign(
        client_id=settings.ENSIGN['CLIENT_ID'],
        client_secret=settings.ENSIGN['CLIENT_SECRET'],
    )

    # Get the status from the ensign server
    _, version, _, _, _ = await client.client.status()
    print(f"sucessfully connected to Ensign version {version}")

    topics = [
        settings.ENSIGN["INSTANCES_TOPIC"],
        settings.ENSIGN["INFERENCES_TOPIC"],
    ]

    # Check that the topics exist
    for topic in topics:
        exists = await client.topic_exists(topic)
        if not exists:
            raise RuntimeError(f"{topic} topic does not exist")

    return client

@async_to_sync
async def publish_review(review):
    client = Ensign(
        client_id=settings.ENSIGN['CLIENT_ID'],
        client_secret=settings.ENSIGN['CLIENT_SECRET'],
    )

    event = review.event()

    try:
        async with asyncio.timeout(5):
            await client.publish(INSTANCES, event, on_ack=on_ack, on_nack=on_ack)
    except TimeoutError:
        print("canceled publish task")


async def on_ack(ack):
    print(ack)