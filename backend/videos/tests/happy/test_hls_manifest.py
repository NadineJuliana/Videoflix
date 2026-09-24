"""
Happy path tests for the HLS manifest endpoint.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import override_settings

from videos.models import Video


class HLSManifestAuthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/video/1/480p/index.m3u8"
        self.user = get_user_model().objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpassword123",
        )

    def test_hls_manifest_returns_existing_manifest(self):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                with patch("videos.signals.django_rq.get_queue"):
                    video = Video.objects.create(  # pylint: disable=no-member
                        title="Test Movie",
                        description="Test Description",
                        video_file="videos/test.mp4",
                        category="Drama",
                    )

                manifest_dir = (
                    Path(media_root)
                    / "hls"
                    / str(video.id)
                    / "480p"
                )
                manifest_dir.mkdir(parents=True)

                manifest_path = manifest_dir / "index.m3u8"
                manifest_path.write_text(
                    "#EXTM3U\n#EXT-X-ENDLIST\n",
                    encoding="utf-8",
                )

                refresh = RefreshToken.for_user(self.user)
                self.client.cookies["access_token"] = str(
                    refresh.access_token
                )

                response = self.client.get(
                    f"/api/video/{video.id}/480p/index.m3u8"
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )

                self.assertEqual(
                    response["Content-Type"],
                    "application/vnd.apple.mpegurl",
                )

                content = b"".join(
                    response.streaming_content
                ).decode("utf-8")

                self.assertEqual(
                    content,
                    "#EXTM3U\n#EXT-X-ENDLIST\n",
                )
