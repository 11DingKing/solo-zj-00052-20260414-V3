from rest_framework import serializers

from tasks.models import Comment, Like, Task


class TaskSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=Task.Status.choices,
        help_text="Task status: pending, in_progress, done",
    )
    priority = serializers.ChoiceField(
        choices=Task.Priority.choices,
        help_text="Task priority: low, medium, high",
    )
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "created_at",
            "updated_at",
            "comments_count",
            "likes_count",
        ]
        read_only_fields = ["created_at", "updated_at", "comments_count", "likes_count"]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_likes_count(self, obj):
        return obj.likes.count()


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Comment
        fields = [
            "id",
            "task",
            "user",
            "username",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "username", "created_at", "updated_at"]


class LikeSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Like
        fields = ["id", "task", "user", "username", "created_at"]
        read_only_fields = ["user", "username", "created_at"]
