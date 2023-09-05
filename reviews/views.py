from rest_framework import viewsets
from rest_framework import permissions
from django.views.generic import TemplateView

from reviews.models import Review
from reviews.serializers import ReviewSerializer


# Create your views here.
class HomePage(TemplateView):

    template_name = "home.html"


class ReviewsViewSet(viewsets.ModelViewSet):

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]