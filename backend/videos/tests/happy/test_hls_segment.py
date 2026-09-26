"""
Happy path tests for the HLS segment endpoint.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from videos.models import Video


class HLSSegmentAuthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpassword123",
        )

    def test_hls_segment_returns_existing_segment(self):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                with patch("videos.signals.django_rq.get_queue"):
                    video = Video.objects.create(  # pylint: disable=no-member
                        title="Test Movie",
                        description="Test Description",
                        video_file="videos/test.mp4",
                        category="Drama",
                    )

                segment_dir = (
                    Path(media_root)
                    / "hls"
                    / str(video.id)
                    / "480p"
                )
                segment_dir.mkdir(parents=True)

                segment_path = segment_dir / "000.ts"
                segment_path.write_bytes(b"test-video-segment")

                refresh = RefreshToken.for_user(self.user)
                self.client.cookies["access_token"] = str(
                    refresh.access_token
                )

                response = self.client.get(
                    f"/api/video/{video.id}/480p/000.ts/"
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )

                self.assertEqual(
                    response["Content-Type"],
                    "video/MP2T",
                )

                content = b"".join(response.streaming_content)

                self.assertEqual(
                    content,
                    b"test-video-segment",
                )
