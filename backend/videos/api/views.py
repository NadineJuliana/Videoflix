"""
API views for videos.
"""

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.authentication import CookieJWTAuthentication
from videos.api.serializers import VideoSerializer
from videos.models import Video
from videos.utils import get_hls_file_path


class VideoListView(APIView):
    """Return video metadata for authenticated users."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all videos ordered by creation date descending."""

        videos = Video.objects.all().order_by(  # pylint: disable=no-member
            "-created_at"
        )
        serializer = VideoSerializer(
            videos,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class HLSManifestView(APIView):
    """Serve HLS manifest files for authenticated users."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, _request, movie_id, resolution):
        """Return the HLS manifest for the requested resolution."""

        video = get_object_or_404(Video, pk=movie_id)
        manifest_path = get_hls_file_path(
            video.id,
            resolution,
            "index.m3u8",
        )

        if not manifest_path.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            open(manifest_path, "rb"),
            content_type="application/vnd.apple.mpegurl",
        )


class HLSSegmentView(APIView):
    """Serve HLS video segments for authenticated users."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, _request, movie_id, resolution, segment):
        """Return the requested HLS transport stream segment."""

        video = get_object_or_404(Video, pk=movie_id)
        segment_path = get_hls_file_path(
            video.id,
            resolution,
            segment,
        )

        if not segment_path.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            open(segment_path, "rb"),
            content_type="video/MP2T",
        )
