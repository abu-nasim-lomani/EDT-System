# core/admin.py

from django.contrib import admin
from .models import Meeting, Task, Project, ChangeLog, Notification


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_time', 'status', 'created_at')
    list_filter = ('status', 'meeting_type')
    search_fields = ('title',)
    filter_horizontal = ('participants',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'meeting', 'owner', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority', 'owner', 'project')
    search_fields = ('title', 'description')
    filter_horizontal = ('responsible_persons', 'events')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_manager', 'start_date', 'end_date', 'created_at')
    list_filter = ('project_manager',)
    search_fields = ('title', 'description')
    filter_horizontal = ('project_employees',)


@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ('model_type', 'object_id', 'action', 'changed_by', 'timestamp')
    list_filter = ('model_type', 'action', 'changed_by')
    search_fields = ('model_type',)
    readonly_fields = ('timestamp',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')