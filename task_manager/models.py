from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TaskList(models.Model):
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_lists')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(max_length=20)
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ManyToManyField(User, related_name='assigned_tasks')

    def __str__(self):
        return self.title

    def is_overdue(self):
        if self.deadline:
            return timezone.now() > self.deadline
        return False
