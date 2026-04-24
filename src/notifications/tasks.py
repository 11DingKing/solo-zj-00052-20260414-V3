import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from notifications.models import Notification

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task
def send_notification_task(
    recipient_id,
    actor_id,
    notification_type,
    object_id,
):
    """
    Asynchronously create or update a notification.
    
    Business rules:
    1. User cannot receive notification from their own action
    2. Same action (same actor + same recipient + same type + same object) only keeps the latest one
       - If exists, update is_read=False and created_at to now
       - If not exists, create new
    """
    try:
        recipient = User.objects.get(id=recipient_id)
        actor = User.objects.get(id=actor_id)

        if recipient == actor:
            logger.info(
                f"Skipping notification: recipient and actor are the same user (id={recipient_id})"
            )
            return

        with transaction.atomic():
            notification, created = Notification.objects.select_for_update().get_or_create(
                recipient=recipient,
                actor=actor,
                notification_type=notification_type,
                object_id=object_id,
                defaults={
                    "is_read": False,
                    "created_at": timezone.now(),
                }
            )

            if not created:
                notification.is_read = False
                notification.created_at = timezone.now()
                notification.save(update_fields=["is_read", "created_at"])
                logger.info(
                    f"Notification updated: {actor.username} -> {recipient.username} ({notification_type})"
                )
            else:
                logger.info(
                    f"Notification created: {actor.username} -> {recipient.username} ({notification_type})"
                )

    except User.DoesNotExist:
        logger.error(f"User not found when creating notification: recipient={recipient_id}, actor={actor_id}")
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")


@shared_task
def send_comment_notification(task_id, actor_id, comment_id=None):
    """
    Send notification when a comment is created.
    The notification goes to the task owner.
    
    Uses task.id as object_id for deduplication.
    """
    from tasks.models import Task

    try:
        task = Task.objects.get(id=task_id)

        if not task.user:
            logger.info(f"Skipping comment notification: Task {task.id} has no owner")
            return

        if task.user.id == actor_id:
            logger.info(
                f"Skipping comment notification: User {actor_id} commented on their own task {task.id}"
            )
            return

        send_notification_task.delay(
            recipient_id=task.user.id,
            actor_id=actor_id,
            notification_type=Notification.NotificationType.COMMENT,
            object_id=task.id,
        )

        logger.info(
            f"Comment notification queued: user {actor_id} commented on task {task.id} owned by {task.user.id}"
        )

    except Task.DoesNotExist:
        logger.error(f"Task not found: {task_id}")
    except Exception as e:
        logger.error(f"Error sending comment notification: {str(e)}")


@shared_task
def send_like_notification(task_id, actor_id, like_id=None):
    """
    Send notification when a like is created.
    The notification goes to the task owner.
    
    Uses task.id as object_id for deduplication.
    """
    from tasks.models import Task

    try:
        task = Task.objects.get(id=task_id)

        if not task.user:
            logger.info(f"Skipping like notification: Task {task.id} has no owner")
            return

        if task.user.id == actor_id:
            logger.info(
                f"Skipping like notification: User {actor_id} liked their own task {task.id}"
            )
            return

        send_notification_task.delay(
            recipient_id=task.user.id,
            actor_id=actor_id,
            notification_type=Notification.NotificationType.LIKE,
            object_id=task.id,
        )

        logger.info(
            f"Like notification queued: user {actor_id} liked task {task.id} owned by {task.user.id}"
        )

    except Task.DoesNotExist:
        logger.error(f"Task not found: {task_id}")
    except Exception as e:
        logger.error(f"Error sending like notification: {str(e)}")
