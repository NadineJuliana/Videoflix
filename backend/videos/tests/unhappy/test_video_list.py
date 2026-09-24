"""
Unhappy path tests for the video list endpoint.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class VideoListUnauthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/video/"

    def test_video_list_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
