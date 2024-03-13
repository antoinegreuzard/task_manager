from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from .common_setup import CommonSetUp
from task_manager.models import Category, TaskList


class ViewTestCase(CommonSetUp):
    def setUp(self):
        super().setUp()
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


class UserAuthenticationTestCase(CommonSetUp):
    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login_and_logout(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': '12345',
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class CategoryTestCase(CommonSetUp):
    def test_create_category(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('create_category'), {'name': 'New Category'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='New Category').exists())

    def test_update_category(self):
        self.client.login(username='testuser', password='12345')
        category = Category.objects.create(name='Old Category', created_by=self.user)
        response = self.client.post(reverse('update_category', args=[category.id]), {'name': 'Updated Category'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='Updated Category').exists())

    def test_delete_category(self):
        self.client.login(username='testuser', password='12345')
        category = Category.objects.create(name='Delete Category', created_by=self.user)
        response = self.client.post(reverse('delete_category', args=[category.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Category.objects.filter(name='Delete Category').exists())


class ShareTaskListTestCase(CommonSetUp):
    def test_share_task_list(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('share_task_list', args=[self.task_list.id]),
                                    {'email': self.other_user.email})
        self.assertEqual(response.status_code, 302, msg="Expected redirection after successful sharing")
        updated_task_list = TaskList.objects.get(id=self.task_list.id)
        self.assertTrue(updated_task_list.shared_with.filter(username='otheruser').exists(),
                        msg="User should have been added to shared_with")
