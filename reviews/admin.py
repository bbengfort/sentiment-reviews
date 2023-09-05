from django.contrib import admin
from reviews.models import Review

class ReviewAdmin(admin.ModelAdmin):
    pass

# Register your models here.
admin.site.register(Review, ReviewAdmin)