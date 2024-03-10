import json

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView

from task_manager.forms import TaskListForm, TaskForm, UserRegistrationForm, UserLoginForm, ShareTaskListForm
from task_manager.models import TaskList, Task


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
        user = self.request.user
        queryset = TaskList.objects.filter(Q(created_by=user) | Q(shared_with=user)).distinct()
        queryset = queryset.annotate(
            total_tasks=Count('tasks'),
            completed_tasks=Count('tasks', filter=Q(tasks__completed=True)),
            not_completed_tasks=Count('tasks', filter=Q(tasks__completed=False)),
        )
        return queryset


class UpdateTaskListView(LoginRequiredMixin, UpdateView):
    model = TaskList
    form_class = TaskListForm
    template_name = 'task_manager/update_task_list.html'
    success_url = reverse_lazy('task_lists')

    def get_queryset(self):
        user = self.request.user
        return TaskList.objects.filter(Q(created_by=user) | Q(shared_with=user)).distinct()


class DeleteTaskListView(LoginRequiredMixin, DeleteView):
    model = TaskList
    template_name = 'task_manager/delete_task_list.html'
    success_url = reverse_lazy('task_lists')

    def get_queryset(self):
        return TaskList.objects.filter(created_by=self.request.user)


def home(request):
    context = {}
    if request.user.is_authenticated:
        user_tasks = Task.objects.filter(
            assigned_to=request.user,
            completed=False,
            deadline__isnull=False
        ).select_related('task_list').prefetch_related('assigned_to').order_by('deadline')

        tasks_data = []
        for task in user_tasks:
            priority_colors = {
                'High': '#ff0000',
                'Medium': '#ffa500',
                'Low': '#008000',
            }
            color = priority_colors.get(task.priority, '#007bff')

            assigned_to_name = task.assigned_to.first().username if task.assigned_to.exists() else 'N/A'
            assigned_to_names = ', '.join(user.username for user in task.assigned_to.all())

            task_data = {
                'id': task.id,
                'title': f"{task.title} ({task.task_list.title} - {assigned_to_name})",
                'start': task.deadline.strftime("%Y-%m-%dT%H:%M:%S"),
                'color': color,
                'extendedProps': {
                    'title': task.title,
                    'description': task.description,
                    'priority': task.priority,
                    'assignedTo': assigned_to_names,
                    'completed': task.completed,
                    'taskListTitle': task.task_list.title,
                }
            }
            tasks_data.append(task_data)

        context['tasks_json'] = json.dumps(tasks_data)
    return render(request, 'home.html', context)


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


class LoginView(FormView):
    form_class = UserLoginForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        if form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(1209600)
        else:
            self.request.session.set_expiry(0)

        next_url = self.request.GET.get('next', '')
        if next_url:
            return HttpResponseRedirect(next_url)
        else:
            return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Username or password is not correct')
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


def user_logout(request):
    logout(request)
    return redirect('home')


class TaskListDetailView(LoginRequiredMixin, DetailView):
    model = TaskList
    context_object_name = 'task_list'
    template_name = 'task_manager/view_task_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = self.object.tasks.all()

        user_id = self.request.GET.get('user_id')
        date = self.request.GET.get('date')
        sort_order = self.request.GET.get('sort', 'deadline')
        completed = self.request.GET.get('completed', 'False')
        priority = self.request.GET.get('priority')

        if user_id:
            tasks = tasks.filter(assigned_to__id=user_id)
        if date:
            tasks = tasks.filter(deadline__date=date)
        if completed == 'True':
            tasks = tasks.filter(completed=True)
        elif completed == 'False':
            tasks = tasks.filter(completed=False)
        elif completed == 'All':
            tasks = self.object.tasks.all()

        if sort_order:
            tasks = tasks.order_by(sort_order)
        if priority:
            tasks = tasks.filter(priority=priority)

        context['tasks'] = tasks
        context['users'] = User.objects.all()
        return context


@login_required
def create_task(request, task_list_id):
    try:
        task_list = TaskList.objects.get(Q(pk=task_list_id), Q(created_by=request.user) | Q(shared_with=request.user))
    except TaskList.DoesNotExist:
        return HttpResponseForbidden("You do not have permission to access this task list.")

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.task_list = task_list
            new_task.save()
            form.save_m2m()
            return redirect('view_task_list', pk=task_list_id)
    else:
        form = TaskForm()
    return render(request, 'task_manager/create_task.html', {'form': form})


@login_required
def update_task(request, task_list_id, task_id):
    task_list = get_object_or_404(TaskList, pk=task_list_id)
    if not (request.user == task_list.created_by or request.user in task_list.shared_with.all()):
        return HttpResponseForbidden("You do not have permission to update this task.")

    task = get_object_or_404(Task, pk=task_id, task_list=task_list)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('view_task_list', pk=task_list_id)
    else:
        form = TaskForm(instance=task)
    return render(request, 'task_manager/update_task.html', {'form': form, 'task': task})


@login_required
def delete_task(request, task_list_id, task_id):
    task_list = get_object_or_404(TaskList, pk=task_list_id)
    if not (request.user == task_list.created_by or request.user in task_list.shared_with.all()):
        return HttpResponseForbidden("You do not have permission to delete this task.")

    task = get_object_or_404(Task, pk=task_id, task_list=task_list)
    if request.method == 'POST':
        task.delete()
        return redirect('view_task_list', pk=task_list_id)
    return render(request, 'task_manager/delete_task.html', {'task': task})


@login_required
def mark_task_completed(request, task_list_id, task_id):
    task_list = get_object_or_404(TaskList, pk=task_list_id)
    # Vérifiez si l'utilisateur a le droit de marquer la tâche comme complétée
    if not (request.user == task_list.created_by or request.user in task_list.shared_with.all()):
        return HttpResponseForbidden("You do not have permission to complete this task.")

    task = get_object_or_404(Task, pk=task_id, task_list=task_list)
    if request.method == 'POST':
        task.completed = not task.completed
        task.save()
    return redirect('view_task_list', pk=task_list_id)


@login_required
def share_task_list(request, task_list_id):
    task_list = get_object_or_404(TaskList, pk=task_list_id, created_by=request.user)
    if request.method == 'POST':
        form = ShareTaskListForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user_to_share_with = User.objects.get(email=email)
                task_list.shared_with.add(user_to_share_with)
                messages.success(request, 'List shared successfully.')
            except ObjectDoesNotExist:
                messages.error(request, 'User does not exist.')
    else:
        form = ShareTaskListForm()
    return render(request, 'task_manager/share_task_list.html', {'form': form})


def custom_404(request, exception):
    """Redirect to home page on 404 errors."""
    return redirect('home')
