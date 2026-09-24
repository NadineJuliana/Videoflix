"""
API views for videos.
"""

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
