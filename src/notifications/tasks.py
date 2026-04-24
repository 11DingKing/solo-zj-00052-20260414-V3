import logging

from celery import shared_task
from django.contrib.auth import get_user_model

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
    Asynchronously create a notification.
    This ensures the notification doesn't block the main request.
    
    Business rules:
    1. User cannot receive notification from their own action
    2. Same action cannot trigger duplicate notification
    """
    try:
        recipient = User.objects.get(id=recipient_id)
        actor = User.objects.get(id=actor_id)

        if recipient == actor:
            logger.info(
                f"Skipping notification: recipient and actor are the same user (id={recipient_id})"
            )
            return

        notification, created = Notification.objects.get_or_create(
            recipient=recipient,
            actor=actor,
            notification_type=notification_type,
            object_id=object_id,
        )

        if created:
            logger.info(
                f"Notification created: {actor.username} -> {recipient.username} ({notification_type})"
            )
        else:
            logger.info(
                f"Notification already exists: {actor.username} -> {recipient.username} ({notification_type})"
            )

    except User.DoesNotExist:
        logger.error(f"User not found when creating notification: recipient={recipient_id}, actor={actor_id}")
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")


@shared_task
def send_comment_notification(comment_id, actor_id):
    """
    Send notification when a comment is created.
    The notification goes to the task owner.
    """
    from tasks.models import Comment

    try:
        comment = Comment.objects.get(id=comment_id)
        task = comment.task

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
            object_id=comment.id,
        )

        logger.info(
            f"Comment notification queued: user {actor_id} commented on task {task.id} owned by {task.user.id}"
        )

    except Comment.DoesNotExist:
        logger.error(f"Comment not found: {comment_id}")
    except Exception as e:
        logger.error(f"Error sending comment notification: {str(e)}")


@shared_task
def send_like_notification(like_id, actor_id):
    """
    Send notification when a like is created.
    The notification goes to the task owner.
    """
    from tasks.models import Like

    try:
        like = Like.objects.get(id=like_id)
        task = like.task

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
            object_id=like.id,
        )

        logger.info(
            f"Like notification queued: user {actor_id} liked task {task.id} owned by {task.user.id}"
        )

    except Like.DoesNotExist:
        logger.error(f"Like not found: {like_id}")
    except Exception as e:
        logger.error(f"Error sending like notification: {str(e)}")
