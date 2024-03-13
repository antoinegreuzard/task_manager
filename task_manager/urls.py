from django.contrib.sitemaps.views import sitemap
from django.urls import path

from task_manager import views
from task_manager.sitemaps import StaticViewSitemap

urlpatterns = [
    path('task_lists/', views.TaskListView.as_view(), name='task_lists'),
    path('create_task_list/', views.CreateTaskListView.as_view(), name='create_task_list'),
    path('task_list/<int:pk>/', views.TaskListDetailView.as_view(), name='view_task_list'),
    path('task_list/<int:pk>/update/', views.UpdateTaskListView.as_view(), name='update_task_list'),
    path('task_list/<int:pk>/delete/', views.DeleteTaskListView.as_view(), name='delete_task_list'),
    path('task_list/<int:pk>/share/', views.ShareTaskListView.as_view(), name='share_task_list'),
    path('', views.HomeView.as_view(), name='home'),
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.LogoutView.as_view(), name='logout'),
    path('task_list/<int:task_list_id>/create_task/', views.CreateTaskView.as_view(), name='create_task'),
    path('task_list/<int:task_list_id>/update_task/<int:pk>/', views.UpdateTaskView.as_view(), name='update_task'),
    path('task_list/<int:task_list_id>/delete_task/<int:pk>/', views.DeleteTaskView.as_view(), name='delete_task'),
    path('task_list/<int:task_list_id>/completed/<int:pk>/', views.MarkTaskCompletedView.as_view(),
         name='mark_task_completed'),
    path('categories/create/', views.CreateCategoryView.as_view(), name='create_category'),
    path('categories/<int:pk>/update/', views.UpdateCategoryView.as_view(), name='update_category'),
    path('categories/<int:pk>/delete/', views.DeleteCategoryView.as_view(), name='delete_category'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
]

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns += [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')
]
