from django.test import TestCase
from django.contrib.auth.models import User
from task_manager.models import TaskList


class CommonSetUp(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', email='otheruser@example.com',
                                                   password='67890')
        self.task_list = TaskList.objects.create(title="Test List", created_by=self.user)
