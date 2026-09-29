"""
Serializers for the videos API.
"""

from rest_framework import serializers

from videos.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serialize video metadata for the video dashboard."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        """Configure serialized fields for videos."""

        model = Video
        fields = (
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail_url",
            "category",
        )

    def get_thumbnail_url(self, obj):
        """Return the absolute thumbnail URL when available."""

        request = self.context.get("request")

        if not obj.thumbnail:
            return None

        if request:
            return request.build_absolute_uri(obj.thumbnail.url)

        return obj.thumbnail.url
