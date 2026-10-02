"""
Utility functions for video workflows.
"""

import shutil
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


def delete_video_file(file_field):
    """Delete a media file if it exists."""

    if file_field and file_field.name:
        file_field.delete(save=False)


def delete_hls_directory(video_id):
    """Delete all generated HLS files for a video."""

    hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(video_id)

    if hls_dir.exists():
        shutil.rmtree(hls_dir)
