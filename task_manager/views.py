import json

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView

from task_manager.forms import TaskListForm, TaskForm, UserRegistrationForm, UserLoginForm, ShareTaskListForm, \
    CategoryForm
from task_manager.models import TaskList, Task, Category


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
        category_id = self.request.GET.get('category')
        queryset = TaskList.objects.filter(Q(created_by=user) | Q(shared_with=user)).distinct()
        queryset = queryset.annotate(
            total_tasks=Count('tasks'),
            completed_tasks=Count('tasks', filter=Q(tasks__completed=True)),
            not_completed_tasks=Count('tasks', filter=Q(tasks__completed=False)),
        )
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(created_by=self.request.user)
        return context


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


class HomeView(View):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

    @staticmethod
    def get_context_data(request):
        context = {}
        if request.user.is_authenticated:
            user_tasks = Task.objects.filter(
                Q(assigned_to=request.user, completed=False, deadline__isnull=False) |
                Q(task_list__shared_with=request.user, assigned_to=request.user, completed=False,
                  deadline__isnull=False)
            ).select_related('task_list').prefetch_related('assigned_to').order_by('deadline')

            tasks_data = []
            for task in user_tasks:
                priority_colors = {
                    'High': '#ff0000',
                    'Medium': '#ffa500',
                    'Low': '#008000',
                }
                color = priority_colors.get(task.priority, '#007bff')

                assigned_to_name = ', '.join(user.username for user in task.assigned_to.all())

                task_data = {
                    'id': task.id,
                    'title': f"{task.title} ({task.task_list.title} - {assigned_to_name})",
                    'start': task.deadline.strftime("%Y-%m-%dT%H:%M:%S"),
                    'color': color,
                    'extendedProps': {
                        'title': task.title,
                        'description': task.description,
                        'priority': task.priority,
                        'assignedTo': assigned_to_name,
                        'completed': task.completed,
                        'taskListTitle': task.task_list.title,
                    }
                }
                tasks_data.append(task_data)

            context['tasks_json'] = json.dumps(tasks_data)
        return context


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
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
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


class LogoutView(View):
    @staticmethod
    def get(request, *args, **kwargs):
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


class CreateTaskView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_manager/create_task.html'

    def dispatch(self, request, *args, **kwargs):
        self.task_list = get_object_or_404(TaskList, Q(pk=kwargs['task_list_id']),
                                           Q(created_by=self.request.user) | Q(shared_with=self.request.user))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.task_list = self.task_list
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('view_task_list', kwargs={'pk': self.task_list.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'task_list': self.task_list})
        return kwargs


class UpdateTaskView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_manager/update_task.html'

    def dispatch(self, request, *args, **kwargs):
        self.task_list = get_object_or_404(TaskList, pk=kwargs['task_list_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Task.objects.filter(task_list=self.task_list, task_list__created_by=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'task_list': self.task_list})
        return kwargs

    def get_success_url(self):
        return reverse_lazy('view_task_list', kwargs={'pk': self.task_list.pk})


class DeleteTaskView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'task_manager/delete_task.html'

    def dispatch(self, request, *args, **kwargs):
        self.task_list_id = kwargs['task_list_id']
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Task.objects.filter(task_list__pk=self.task_list_id, task_list__created_by=self.request.user)

    def get_success_url(self):
        return reverse_lazy('view_task_list', kwargs={'pk': self.task_list_id})


class MarkTaskCompletedView(LoginRequiredMixin, View):
    @staticmethod
    def post(request, task_list_id, task_id, *args, **kwargs):
        task = get_object_or_404(Task, pk=task_id, task_list__id=task_list_id, task_list__created_by=request.user)
        task.completed = not task.completed
        task.save()
        return redirect('view_task_list', pk=task_list_id)


class ShareTaskListView(LoginRequiredMixin, FormView):
    form_class = ShareTaskListForm
    template_name = 'task_manager/share_task_list.html'

    def dispatch(self, request, *args, **kwargs):
        self.task_list = get_object_or_404(TaskList, pk=kwargs['task_list_id'], created_by=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user_to_share_with = User.objects.get(email=email)
            self.task_list.shared_with.add(user_to_share_with)
            messages.success(self.request, 'List shared successfully.')
        except User.DoesNotExist:
            messages.error(self.request, 'User does not exist.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('view_task_list', kwargs={'pk': self.task_list.pk})


class CreateCategoryView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'task_manager/create_category.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class UpdateCategoryView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'task_manager/update_category.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        return Category.objects.filter(created_by=self.request.user)


class DeleteCategoryView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'task_manager/delete_category.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        return Category.objects.filter(created_by=self.request.user)


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'task_manager/category_list.html'

    def get_queryset(self):
        return Category.objects.filter(created_by=self.request.user)


def custom_404(request, exception):
    """Redirect to home page on 404 errors."""
    return redirect('home')
