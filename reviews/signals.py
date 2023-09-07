from reviews.models import Review
from django.dispatch import receiver
from reviews.ensign import publish_review
from django.db.models.signals import post_save


@receiver(post_save, sender=Review, dispatch_uid="publish_instance_event")
def publish_instance_event(sender, instance, **kwargs):
    publish_review(instance)