from django.test import TestCase, Client
from django.urls import reverse
from task_manager.models import TaskList, Task
from django.utils import timezone
from django.contrib.auth.models import User


class CommonSetUp(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.task_list = TaskList.objects.create(title="Test List", created_by=self.user)


class TaskListAndTaskModelTest(CommonSetUp):
    def test_task_list_creation(self):
        self.assertTrue(isinstance(self.task_list, TaskList))
        self.assertEqual(self.task_list.__str__(), "Test List")

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
        self.assertEqual(task.__str__(), "Test Task")
        self.assertFalse(task.is_overdue())


class ViewTestCase(CommonSetUp):
    def setUp(self):
        super().setUp()  # Appelle setUp de CommonSetUp pour réutiliser la configuration
        self.client = Client()
        self.client.login(username='testuser', password='12345')

    def test_task_list_view(self):
        response = self.client.get(reverse('task_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task_list.title)

    def test_create_task_list_view(self):
        response = self.client.post(reverse('create_task_list'), {'title': 'New List'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New List")
