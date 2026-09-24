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
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/video/"
        self.user = get_user_model().objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpassword123",
        )

    def test_authenticated_user_can_access_video_list(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["access_token"] = str(refresh.access_token)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_video_list_returns_video_data(self):
        video = Video.objects.create(  # pylint: disable=no-member
            title="Test Movie",
            description="Test Description",
            video_file="videos/test.mp4",
            thumbnail="thumbnails/test.jpg",
            category="Drama",
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["access_token"] = str(refresh.access_token)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], video.id)
        self.assertEqual(response.data[0]["title"], "Test Movie")
        self.assertEqual(
            response.data[0]["description"],
            "Test Description",
        )
        self.assertEqual(response.data[0]["category"], "Drama")
        self.assertIn("created_at", response.data[0])
        self.assertIn("thumbnail_url", response.data[0])

    def test_video_list_is_ordered_by_created_at_desc(self):
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

        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["access_token"] = str(refresh.access_token)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], newer_video.id)
        self.assertEqual(response.data[1]["id"], older_video.id)
