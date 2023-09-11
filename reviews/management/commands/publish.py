from django.conf import settings
from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand, CommandError

from reviews.models import Review
from pyensign.ensign import Ensign


class Command(BaseCommand):

    help = "publishes the specified review for prediction"

    def add_arguments(self, parser):
        parser.add_argument("review_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        reviews = []
        for review_id in options["review_ids"]:
            try:
                review = Review.objects.get(pk=review_id)
                reviews.append(review.event())
            except Review.DoesNotExist:
                raise CommandError(f"review {review_id} does not exist")

        publish(reviews)

        self.stdout.write(
            self.style.SUCCESS(f"published {len(reviews)} reviews")
        )

@async_to_sync
async def publish(events):
    client = Ensign(
        client_id=settings.ENSIGN['CLIENT_ID'],
        client_secret=settings.ENSIGN['CLIENT_SECRET'],
    )

    instances = settings.ENSIGN["INSTANCES_TOPIC"]

    # Get the status from the ensign server
    _, version, _, _, _ = await client.client.status()
    print(f"sucessfully connected to Ensign version {version}")

    for event in events:
        await client.publish(instances, event)
        _ = await event.wait_for_ack()