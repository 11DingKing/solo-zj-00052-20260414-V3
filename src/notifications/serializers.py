from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_username = serializers.ReadOnlyField(source="actor.username")

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "actor",
            "actor_username",
            "notification_type",
            "object_id",
            "is_read",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "recipient",
            "actor",
            "actor_username",
            "notification_type",
            "object_id",
            "created_at",
        ]


class NotificationCountSerializer(serializers.Serializer):
    unread_count = serializers.IntegerField()
