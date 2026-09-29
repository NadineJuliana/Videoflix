"""
Application configuration for videos.
"""

from django.apps import AppConfig


class VideosConfig(AppConfig):
    """Configure the videos application and register its signals."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videos'

    def ready(self):
        """Register video signal handlers when the app is ready."""

        import videos.signals  # pylint: disable=import-outside-toplevel,unused-import
