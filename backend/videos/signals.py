"""
Signals for video processing.
"""

import django_rq
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from videos.models import Video
from videos.tasks import process_video_task
from videos.utils import delete_hls_directory, delete_video_file


@receiver(post_save, sender=Video)
def enqueue_video_processing(sender, instance, created, **_kwargs):  # pylint: disable=unused-argument
    """Queue video processing after a new video is created."""

    if not created:
        return

    queue = django_rq.get_queue("default", autocommit=True)
    queue.enqueue(process_video_task, instance.id)


@receiver(post_delete, sender=Video)
def delete_video_media(sender, instance, **_kwargs):  # pylint: disable=unused-argument
    """Delete all media files associated with a deleted video."""

    delete_video_file(instance.video_file)
    delete_video_file(instance.thumbnail)
    delete_hls_directory(instance.id)
