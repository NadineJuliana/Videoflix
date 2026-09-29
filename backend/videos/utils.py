"""
Utility functions for video workflows.
"""

from pathlib import Path

from django.conf import settings


def get_hls_file_path(video_id, resolution, filename):
    """Return the path to an HLS file for a video resolution."""
    return (
        Path(settings.MEDIA_ROOT)
        / "hls"
        / str(video_id)
        / resolution
        / filename
    )
