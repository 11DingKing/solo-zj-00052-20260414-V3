from django.test import TestCase

from tasks.models import Task


class TaskModelTest(TestCase):
    def test_create_task(self):
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            status=Task.Status.PENDING,
            priority=Task.Priority.MEDIUM,
        )
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, Task.Status.PENDING)
        self.assertEqual(task.priority, Task.Priority.MEDIUM)

    def test_task_str(self):
        task = Task.objects.create(title="Test Task")
        self.assertEqual(str(task), "Test Task")

    def test_status_choices(self):
        task = Task.objects.create(title="Test")
        task.status = Task.Status.IN_PROGRESS
        task.save()
        self.assertEqual(task.status, "in_progress")

    def test_priority_choices(self):
        task = Task.objects.create(title="Test")
        task.priority = Task.Priority.HIGH
        task.save()
        self.assertEqual(task.priority, "high")
