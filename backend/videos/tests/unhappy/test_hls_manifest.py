"""
Unhappy path tests for the HLS manifest endpoint.
"""

import tempfile
from unittest.mock import patch

from django.test import override_settings

from videos.models import Video
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


class HLSManifestUnauthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/video/1/480p/index.m3u8"

    def test_hls_manifest_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class HLSManifestNotFoundTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpassword123",
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["access_token"] = str(
            refresh.access_token
        )

    def test_hls_manifest_returns_404_for_missing_video(self):
        response = self.client.get(
            "/api/video/999/480p/index.m3u8"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_hls_manifest_returns_404_for_missing_manifest(self):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                with patch("videos.signals.django_rq.get_queue"):
                    video = Video.objects.create(  # pylint: disable=no-member
                        title="Test Movie",
                        description="Test Description",
                        video_file="videos/test.mp4",
                        category="Drama",
                    )

                response = self.client.get(
                    f"/api/video/{video.id}/480p/index.m3u8"
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_404_NOT_FOUND,
                )
