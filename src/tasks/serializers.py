from rest_framework import serializers

from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=Task.Status.choices,
        help_text="Task status: pending, in_progress, done",
    )
    priority = serializers.ChoiceField(
        choices=Task.Priority.choices,
        help_text="Task priority: low, medium, high",
    )

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
        ]
        read_only_fields = ["created_at", "updated_at"]
