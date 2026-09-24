"""
API views for videos.
"""

from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.authentication import CookieJWTAuthentication
from videos.api.serializers import VideoSerializer
from videos.models import Video


class VideoListView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        videos = Video.objects.all().order_by("-created_at")  # pylint: disable=no-member
        serializer = VideoSerializer(
            videos,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class HLSManifestView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        video = get_object_or_404(Video, pk=movie_id)
        manifest_path = (
            Path(settings.MEDIA_ROOT)
            / "hls"
            / str(video.id)
            / resolution
            / "index.m3u8"
        )

        if not manifest_path.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            open(manifest_path, "rb"),
            content_type="application/vnd.apple.mpegurl",
        )
