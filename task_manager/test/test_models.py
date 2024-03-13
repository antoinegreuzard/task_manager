from django.utils import timezone
from .common_setup import CommonSetUp
from task_manager.models import Task, TaskList


class TaskListAndTaskModelTest(CommonSetUp):
    def test_task_list_creation(self):
        self.assertTrue(isinstance(self.task_list, TaskList))
        self.assertEqual(str(self.task_list), "Test List")

    def test_task_creation(self):
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            deadline=timezone.now() + timezone.timedelta(days=1),
            priority="Medium",
            task_list=self.task_list
        )
        task.assigned_to.add(self.user)
        self.assertTrue(isinstance(task, Task))
        self.assertEqual(str(task), "Test Task")
        self.assertFalse(task.is_overdue())
