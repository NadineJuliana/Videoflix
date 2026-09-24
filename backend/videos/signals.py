"""
Signals for video processing.
"""

import django_rq
from django.db.models.signals import post_save
from django.dispatch import receiver

from videos.models import Video
from videos.tasks import process_video_task


@receiver(post_save, sender=Video)
def enqueue_video_processing(sender, instance, created, **_kwargs):  # pylint: disable=unused-argument
    if not created:
        return

    queue = django_rq.get_queue("default", autocommit=True)
    queue.enqueue(process_video_task, instance.id)
