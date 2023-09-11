#!/usr/bin/env python3

import json
import environ
import asyncio
import argparse
import psycopg2

from datetime import datetime
from pyensign.events import Event
from pyensign.ensign import Ensign

env = environ.Env()
environ.Env.read_env(".env")


async def main(args):
    pg = psycopg2.connect(env("DATABASE_URL"))

    with pg.cursor() as cur:
        cur.execute("SELECT id, text, created, modified FROM reviews where id=%s", args.pk)
        row = cur.fetchone()

    if row is None:
        print(f"could not find record with pk {args.pk[0]}")
        return

    data = dict(zip(["id", "text", "created", "modified"], row))
    data['created'] = data['created'].isoformat()
    data['modified'] = data['modified'].isoformat()

    event = Event(
        data=json.dumps(data).encode("utf-8"),
        mimetype="application/json",
        schema_name="Instance",
        schema_version="1.0.0",
        meta={"review_id": str(args.pk[0])}
    )

    client = Ensign(
        client_id=env("ENSIGN_CLIENT_ID"),
        client_secret=env("ENSIGN_CLIENT_SECRET"),
    )

    await client.publish(env("ENSIGN_INSTANCES_TOPIC"), event)
    ack = await event.wait_for_ack()
    print(ack)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="quick publish an event from the database"
    )

    parser.add_argument("pk", nargs=1, type=int)
    args = parser.parse_args()
    asyncio.run(main(args))