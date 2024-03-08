from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from task_manager.models import TaskList, Task
from task_manager.forms import TaskListForm, TaskForm, UserRegistrationForm, UserLoginForm


@login_required
def task_lists(request):
    task_lists = TaskList.objects.filter(created_by=request.user)
    return render(request, 'task_manager/task_lists.html', {'task_lists': task_lists})


class CreateTaskListView(LoginRequiredMixin, CreateView):
    model = TaskList
    form_class = TaskListForm
    template_name = 'task_manager/create_task_list.html'
    success_url = reverse_lazy('task_lists')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Task list created successfully.')
        return super().form_valid(form)


class TaskListView(LoginRequiredMixin, ListView):
    model = TaskList
    context_object_name = 'task_lists'
    template_name = 'task_manager/task_lists.html'

    def get_queryset(self):
        return TaskList.objects.filter(created_by=self.request.user)


class UpdateTaskListView(LoginRequiredMixin, UpdateView):
    model = TaskList
    form_class = TaskListForm
    template_name = 'task_manager/update_task_list.html'
    success_url = reverse_lazy('task_lists')

    def get_queryset(self):
        return TaskList.objects.filter(created_by=self.request.user)


class DeleteTaskListView(LoginRequiredMixin, DeleteView):
    model = TaskList
    template_name = 'task_manager/delete_task_list.html'
    success_url = reverse_lazy('task_lists')

    def get_queryset(self):
        return TaskList.objects.filter(created_by=self.request.user)


def home(request):
    return render(request, 'home.html')


class RegisterView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        form = UserRegistrationForm()
        return render(request, 'registration/register.html', {'form': form})

    @staticmethod
    def post(request, *args, **kwargs):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
        return render(request, 'registration/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                if form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(1209600)
                else:
                    request.session.set_expiry(0)

                return redirect('home')
            else:
                messages.error(request, 'Username or password is not correct')
        else:
            messages.error(request, 'Error validating the form')
    else:
        form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


class TaskListDetailView(LoginRequiredMixin, DetailView):
    model = TaskList
    context_object_name = 'task_list'
    template_name = 'task_manager/view_task_list.html'

    def get_queryset(self):
        return TaskList.objects.filter(created_by=self.request.user)


@login_required
def create_task(request, task_list_id):
    task_list = get_object_or_404(TaskList, pk=task_list_id, created_by=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.task_list = task_list
            task.save()
            return redirect('view_task_list', pk=task_list_id)
    else:
        form = TaskForm()
    return render(request, 'task_manager/create_task.html', {'form': form})


@login_required
def update_task(request, task_list_id, task_id):
    task_list = get_object_or_404(TaskList, pk=task_list_id, created_by=request.user)
    task = get_object_or_404(Task, pk=task_id, task_list=task_list)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('view_task_list', pk=task_list_id)
    else:
        form = TaskForm(instance=task)
    return render(request, 'task_manager/update_task.html', {'form': form})


@login_required
def delete_task(request, task_list_id, task_id):
    task_list = get_object_or_404(TaskList, pk=task_list_id, created_by=request.user)
    task = get_object_or_404(Task, pk=task_id, task_list=task_list)
    if request.method == 'POST':
        task.delete()
        return redirect('view_task_list', pk=task_list_id)
    return render(request, 'task_manager/delete_task.html', {'task': task})
