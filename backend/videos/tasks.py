"""
Background tasks for video processing.
"""

from pathlib import Path

from django.conf import settings

from videos.models import Video
from videos.services.video_processing import process_video


def process_video_task(video_id):
    video = Video.objects.get(pk=video_id)  # pylint: disable=no-member

    source_path = video.video_file.path
    hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(video.id)
    thumbnail_path = (
        Path(settings.MEDIA_ROOT) / "thumbnails" / f"{video.id}.jpg"
    )

    process_video(source_path, hls_dir, thumbnail_path)

    video.thumbnail.name = f"thumbnails/{video.id}.jpg"
    video.save(update_fields=["thumbnail"])
