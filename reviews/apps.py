# from reviews.ensign import connect as ensign_connect
from django.apps import AppConfig


class ReviewsConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'

    def ready(self):
        import reviews.signals # noqa
