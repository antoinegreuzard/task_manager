from django.test import TestCase
from task_manager.forms import TaskForm, TaskListForm, CategoryForm, UserRegistrationForm
from task_manager.models import TaskList, User
from django.utils import timezone


class TaskListFormTest(TestCase):
    def test_task_list_form_valid_data(self):
        form = TaskListForm(data={'title': 'New List'})
        self.assertTrue(form.is_valid())

    def test_task_list_form_no_data(self):
        form = TaskListForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)


class TaskFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.task_list = TaskList.objects.create(title="Test List", created_by=self.user)

    def test_task_form_valid_data(self):
        form = TaskForm(data={
            'title': 'New Task',
            'description': 'Test Description',
            'deadline': timezone.now(),
            'priority': 'Medium',
            'assigned_to': [self.user.id],
        }, task_list=self.task_list)
        self.assertTrue(form.is_valid())

    def test_task_form_no_data(self):
        form = TaskForm(data={}, task_list=self.task_list)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors), 1)


class CategoryFormTest(TestCase):
    def test_category_form_valid_data(self):
        form = CategoryForm(data={'name': 'Work'})
        self.assertTrue(form.is_valid())

    def test_category_form_no_data(self):
        form = CategoryForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)


class UserRegistrationFormTest(TestCase):
    def test_user_registration_form_valid_data(self):
        form = UserRegistrationForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123',
        })
        self.assertTrue(form.is_valid())

    def test_user_registration_form_no_data(self):
        form = UserRegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors), 4)
