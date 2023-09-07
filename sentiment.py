#!/usr/bin/env python

import json
import pickle
import environ
import asyncio
import warnings
import argparse
import psycopg2

from pathlib import Path
from pyensign.events import Event
from pyensign.ensign import Ensign

# Ignore warnings
warnings.filterwarnings('ignore')

# Application description
DESCRIPTION = "Async model inferencing for the reviews app"
EPILOG      = "If there are any bugs or concerns, submit an issue on Github"
VERSION     = "%(prog)s v1.0.0"
BASE_DIR    = Path(__file__).resolve().parent

# Read environment variables
env = environ.Env(
    ENSIGN_INSTANCES_TOPIC=(str, "instances"),
    ENSIGN_INFERENCES_TOPIC=(str, "inferences"),
)

environ.Env.read_env(BASE_DIR / ".env")


async def ensign(*topics):
    client = Ensign(
        client_id=env("ENSIGN_CLIENT_ID"),
        client_secret=env("ENSIGN_CLIENT_SECRET"),
    )

    # Get the status from the ensign server
    _, version, _, _, _ = await client.client.status()
    print(f"sucessfully connected to Ensign version {version}")

    # Check that the topics exist
    for topic in topics:
        exists = await client.topic_exists(topic)
        if not exists:
            raise RuntimeError(f"{topic} topic does not exist")

    return client


async def predict(args):
    # Load the model from disk
    with open(args.model, 'rb') as f:
        model = pickle.load(f)
    print(f"{model.__class__.__name__} model loaded from {args.model}")

    # Required topics
    instances = env("ENSIGN_INSTANCES_TOPIC")
    inferences = env("ENSIGN_INFERENCES_TOPIC")

    # Create Ensign client and check topics exist
    client = await ensign(instances, inferences)

    # Subscribe to all incoming instances
    async for event in client.subscribe(instances):
        # Load the instance data and prepare to make a prediction
        instance = json.loads(event.data)
        inference = {
            "id": instance.id,
            "features": None,
        }

        # Make the polarity inference and compute the confidence
        inference["polarity"] = model.predict([instance.text])
        inference["confidence"] = max(model.decision_function([instance.text]))

        # Create the inference event to publish
        out = Event(
            data=json.dumps(inference).encode("utf-8"),
            mimetype="application/json",
            schema_name="Inference",
            schema_version="1.0.0",
            meta={"review_id": str(instance.id)}
        )

        # Publish the out event and ack the incoming event
        await client.publish(inferences, out)
        await event.ack()
        print(f"pridction on review {instance.id} complete")


UPDATE = (
    "UPDATE reviews SET "
    "polarity=%(polarity)s "
    "confidence=%(confidence)s "
    "features=%(features)s "
    "WHERE id=%(id)s;"
)


async def sink(args):
    # Connect to PostgreSQL database
    pg = psycopg2.connect(env("DATABASE_URL"))

    # Required topics
    inferences = env("ENSIGN_INFERENCES_TOPIC")

    # Create Ensign client and check topic exists
    client = await ensign(inferences)

    # Subscribe to the inferences channel and update reviews with prediction
    async for event in client.subscribe(inferences):
        data = json.loads(event.data)
        with pg.cursor() as cur:
            cur.execute(UPDATE, **data)
            cur.commit()

        await event.ack()
        print(f"review {data['id']} updated")


if __name__ == "__main__":
    cmds = [
        {
            "name": "predict",
            "help": "make predictions on incoming instances and publish to inferences topic",
            "func": predict,
            "args": {
                ("-m", "--model"): {
                    "type": str, "default": "fixtures/model.pickle", "metavar": "PATH",
                    "help": "the path to the model pickle file",
                },
            }
        },
        {
            "name": "sink",
            "help": "subscribe to inferences and store them in the application database",
            "func": sink,
            "args": {},
        },
    ]

    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG)
    parser.add_argument('-v', '--version', action="version", version=VERSION)
    subparsers = parser.add_subparsers(help="subcommands")

    for cmd in cmds:
        subparser = subparsers.add_parser(cmd['name'], help=cmd['help'])
        subparser.set_defaults(func=cmd['func'])

        for pargs, kwargs in cmd['args'].items():
            if isinstance(pargs, str):
                pargs = (pargs,)
            subparser.add_argument(*pargs, **kwargs)

    args = parser.parse_args()
    try:
        asyncio.run(args.func(args))
    except (KeyboardInterrupt, RuntimeError):
        print("worker shutdown ...")
    except Exception as e:
        parser.error(str(e))