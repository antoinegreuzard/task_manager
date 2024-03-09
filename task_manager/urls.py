from django.urls import path

from task_manager import views

urlpatterns = [
    path('task_lists/', views.TaskListView.as_view(), name='task_lists'),
    path('create_task_list/', views.CreateTaskListView.as_view(), name='create_task_list'),
    path('task_list/<int:pk>/', views.TaskListDetailView.as_view(), name='view_task_list'),
    path('task_list/<int:pk>/update/', views.UpdateTaskListView.as_view(), name='update_task_list'),
    path('task_list/<int:pk>/delete/', views.DeleteTaskListView.as_view(), name='delete_task_list'),
    path('', views.home, name='home'),
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('task_list/<int:task_list_id>/create_task/', views.create_task, name='create_task'),
    path('task_list/<int:task_list_id>/update_task/<int:task_id>/', views.update_task, name='update_task'),
    path('task_list/<int:task_list_id>/delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('task_list/<int:task_list_id>/completed/<int:task_id>/', views.mark_task_completed,
         name='mark_task_completed'),
]
