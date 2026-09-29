"""
Admin configuration for videos.
"""

from django.contrib import admin

from videos.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Configure video entries in the Django admin."""

    list_display = (
        "id",
        "title",
        "category",
        "created_at",
    )
