from django.urls import path

from task_manager import views

urlpatterns = [
    path('task_lists/', views.TaskListView.as_view(), name='task_lists'),
    path('create_task_list/', views.CreateTaskListView.as_view(), name='create_task_list'),
    path('task_list/<int:pk>/', views.TaskListDetailView.as_view(), name='view_task_list'),
    path('task_list/<int:pk>/update/', views.UpdateTaskListView.as_view(), name='update_task_list'),
    path('task_list/<int:pk>/delete/', views.DeleteTaskListView.as_view(), name='delete_task_list'),
    path('task_list/<int:task_list_id>/share/', views.ShareTaskListView.as_view(), name='share_task_list'),
    path('', views.HomeView.as_view(), name='home'),
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.LogoutView.as_view(), name='logout'),
    path('task_list/<int:task_list_id>/create_task/', views.CreateTaskView.as_view(), name='create_task'),
    path('task_list/<int:task_list_id>/update_task/<int:task_id>/', views.UpdateTaskView.as_view(), name='update_task'),
    path('task_list/<int:task_list_id>/delete_task/<int:task_id>/', views.DeleteTaskView.as_view(), name='delete_task'),
    path('task_list/<int:task_list_id>/completed/<int:task_id>/', views.MarkTaskCompletedView.as_view(),
         name='mark_task_completed'),
]
