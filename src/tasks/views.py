from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.tasks import send_comment_notification, send_like_notification
from tasks.models import Comment, Like, Task
from tasks.serializers import CommentSerializer, LikeSerializer, TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "priority"]
    ordering_fields = ["due_date", "created_at", "updated_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["task"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        task = comment.task
        
        if task.user and task.user.id != self.request.user.id:
            send_comment_notification.delay(
                task_id=task.id,
                actor_id=self.request.user.id,
                comment_id=comment.id,
            )


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["task"]

    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        like = serializer.save(user=self.request.user)
        task = like.task
        
        if task.user and task.user.id != self.request.user.id:
            send_like_notification.delay(
                task_id=task.id,
                actor_id=self.request.user.id,
                like_id=like.id,
            )

    @action(detail=False, methods=["post"])
    def toggle(self, request):
        task_id = request.data.get("task")
        if not task_id:
            return Response(
                {"error": "task is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )

        like, created = Like.objects.get_or_create(
            task=task, user=request.user
        )

        if not created:
            like.delete()
            return Response(
                {"liked": False, "message": "Like removed"},
                status=status.HTTP_200_OK,
            )

        if task.user and task.user.id != request.user.id:
            send_like_notification.delay(
                task_id=task.id,
                actor_id=request.user.id,
                like_id=like.id,
            )

        serializer = self.get_serializer(like)
        return Response(
            {"liked": True, "like": serializer.data},
            status=status.HTTP_201_CREATED,
        )
