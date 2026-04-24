from django.conf import settings
from django.db import models


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        COMMENT = "comment", "Comment"
        LIKE = "like", "Like"
        FOLLOW = "follow", "Follow"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="The user who receives this notification",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        help_text="The user who performed the action",
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        help_text="Type of notification: comment, like, follow",
    )
    object_id = models.BigIntegerField(
        help_text="ID of the related object (task, comment, etc.)",
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the notification has been read",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "is_read"]),
        ]
        unique_together = [
            "recipient",
            "actor",
            "notification_type",
            "object_id",
        ]

    def __str__(self):
        return f"{self.actor} {self.notification_type} -> {self.recipient}"
