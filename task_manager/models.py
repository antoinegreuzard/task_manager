from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TaskList(models.Model):
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_lists')
    shared_with = models.ManyToManyField(User, related_name='shared_task_lists', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(max_length=20)
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ManyToManyField(User, related_name='assigned_tasks')
    completed = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')

    def __str__(self):
        return self.title

    def is_overdue(self):
        if self.deadline:
            return timezone.now() > self.deadline
        return False
