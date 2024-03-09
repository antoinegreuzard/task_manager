# Generated by Django 5.0.3 on 2024-03-09 17:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_lists', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('deadline', models.DateTimeField(blank=True, null=True)),
                ('priority', models.CharField(max_length=20)),
                ('assigned_to', models.ManyToManyField(related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
                ('task_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='task_manager.tasklist')),
            ],
        ),
    ]
