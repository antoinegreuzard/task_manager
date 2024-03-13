from django.urls import reverse
from .common_setup import CommonSetUp


class TaskListPermissionsTest(CommonSetUp):
    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('task_lists'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("task_lists")}')

    def test_user_can_view_own_task_lists(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('task_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task_list.title)

    def test_user_cannot_view_others_task_lists(self):
        self.client.login(username='otheruser', password='67890')
        response = self.client.get(reverse('task_lists'))
        self.assertNotContains(response, self.task_list.title)
