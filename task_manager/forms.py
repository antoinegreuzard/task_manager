from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q

from .models import TaskList, Task, Category


class TaskListForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = TaskList
        fields = ['title']


class TaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 4, 'class': 'form-control'},
        ),
        required=False,
    )
    priority = forms.ChoiceField(
        choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'priority', 'assigned_to', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'priority': forms.Select(choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')]),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        task_list = kwargs.pop('task_list', None)  # Retirer 'task_list' de kwargs
        super(TaskForm, self).__init__(*args, **kwargs)
        if task_list:
            self.fields['assigned_to'].queryset = User.objects.filter(
                Q(id=task_list.created_by.id) | Q(shared_task_lists=task_list)
            ).distinct()


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), required=True)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Password confirmation",
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(strip=False, widget=forms.PasswordInput(
        attrs={'autocomplete': 'current-password', 'class': 'form-control'}))

    class Meta:
        model = User
        fields = '__all__'


class ShareTaskListForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
