import json

from django.db import models
from pyensign.events import Event
from django.utils.translation import gettext_lazy as _


class Polarity(models.TextChoices):

    UNKNOWN  = "UNK", _("Unknown")
    NEGATIVE = "NEG", _("Negative")
    NEUTRAL  = "NEU", _("Neutral")
    POSITIVE = "POS", _("Positive")


class Review(models.Model):

    text = models.TextField(
        max_length=300, null=False, blank=False,
        help_text="The text content of the review to classify",
    )

    polarity = models.CharField(
        max_length=3, null=False, blank=False,
        choices=Polarity.choices, default=Polarity.UNKNOWN,
        help_text="The model inferenced polarity of the review",
    )

    confidence = models.FloatField(
        default=0.0, null=False, blank=False,
        help_text="The confidence of the model at inference time",
    )

    features = models.JSONField(
        null=True, blank=True, default=None,
        help_text="The most informative features for the instance from the model",
    )

    created  = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reviews"
        ordering = ('-created',)
        verbose_name = "review"
        verbose_name_plural = "reviews"

    def __str__(self):
        return self.text

    def event(self):
        data = {
            "id": self.id,
            "text": self.text,
            "created": self.created.isoformat(),
            "modified": self.modified.isoformat(),
        }

        return Event(
            data=json.dumps(data).encode("utf-8"),
            mimetype="application/json",
            schema_name="Instance",
            schema_version="1.0.0",
            meta={"review_id": str(self.id)}
        )
