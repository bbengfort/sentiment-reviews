from reviews.models import Review
from rest_framework import serializers

class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = [
            'polarity', 'confidence', 'features', 'created', 'modified',
        ]