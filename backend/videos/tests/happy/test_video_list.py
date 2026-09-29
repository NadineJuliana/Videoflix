"""
Happy path tests for the video list endpoint.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from videos.models import Video


class VideoListAuthenticatedTests(TestCase):
    """Test authenticated access to the video list."""

    def setUp(self):
        """Create and authenticate a user."""

        self.client = APIClient()
        self.url = "/api/video/"
        self.user = get_user_model().objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpassword123",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["access_token"] = str(
            refresh.access_token
        )

    def test_authenticated_user_can_access_video_list(self):
        """Return HTTP 200 for an authenticated user."""

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_video_list_returns_video_data(self):
        """Return the documented video metadata."""

        video = Video.objects.create(  # pylint: disable=no-member
            title="Test Movie",
            description="Test Description",
            video_file="videos/test.mp4",
            thumbnail="thumbnails/test.jpg",
            category="Drama",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], video.id)
        self.assertEqual(response.data[0]["title"], video.title)
        self.assertEqual(
            response.data[0]["description"],
            video.description,
        )
        self.assertEqual(response.data[0]["category"], video.category)
        self.assertIn("created_at", response.data[0])
        self.assertIn("thumbnail_url", response.data[0])

    def test_video_list_is_ordered_by_created_at_desc(self):
        """Return newer videos before older videos."""

        older_video = Video.objects.create(  # pylint: disable=no-member
            title="Older Movie",
            description="Older Description",
            video_file="videos/older.mp4",
            category="Drama",
        )
        newer_video = Video.objects.create(  # pylint: disable=no-member
            title="Newer Movie",
            description="Newer Description",
            video_file="videos/newer.mp4",
            category="Action",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], newer_video.id)
        self.assertEqual(response.data[1]["id"], older_video.id)
