# core/models.py

from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects'
    )
    project_employees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='projects_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class ChangeLog(models.Model):
    class ModelType(models.TextChoices):
        EVENT = 'EVENT', 'Event'
        TASK = 'TASK', 'Task'
        PROJECT = 'PROJECT', 'Project'

    class ActionType(models.TextChoices):
        CREATE = 'CREATE', 'Create'
        UPDATE = 'UPDATE', 'Update'
        DELETE = 'DELETE', 'Delete'

    model_type = models.CharField(max_length=20, choices=ModelType.choices)
    object_id = models.PositiveIntegerField()
    action = models.CharField(max_length=20, choices=ActionType.choices)
    changes = models.JSONField(default=dict, help_text='Dictionary of field changes')
    timestamp = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='changes_made'
    )

    def __str__(self):
        return f"{self.action} on {self.model_type} #{self.object_id}"

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_type', 'object_id']),
            models.Index(fields=['changed_by', '-timestamp']),
        ]


class Meeting(models.Model):
    class MeetingType(models.TextChoices):
        TEAM = "TEAM", "Team"
        PROJECT = "PROJECT", "Project"
        BRAINSTORM = "BRAINSTORM", "Brainstorm"
        REVIEW = "REVIEW", "Review"

    class MeetingStatus(models.TextChoices):
        UPCOMING = "UPCOMING", "Upcoming"
        COMPLETED = "COMPLETED", "Completed"

    title = models.CharField(max_length=200)
    meeting_time = models.DateTimeField(default=timezone.now)
    duration = models.IntegerField(default=60, help_text="Duration in minutes")
    meeting_type = models.CharField(max_length=20, choices=MeetingType.choices, default=MeetingType.TEAM)
    status = models.CharField(max_length=20, choices=MeetingStatus.choices, default=MeetingStatus.UPCOMING)

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='meetings_participated',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} on {self.meeting_time.strftime('%b %d, %Y at %I:%M %p')}"

    def get_absolute_url(self):
        return reverse('meeting_detail', kwargs={'pk': self.pk})


class Task(models.Model):
    class StatusChoices(models.TextChoices):
        UPCOMING = "UPCOMING", "Upcoming"
        ONGOING = "ONGOING", "In Progress"
        PENDING = "PENDING", "Pending"
        HOLDING = "HOLDING", "On Hold"
        COMPLETED = "COMPLETED", "Completed"

    class PriorityChoices(models.TextChoices):
        HIGH = "HIGH", "High"
        MEDIUM = "MEDIUM", "Medium"
        LOW = "LOW", "Low"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='task_owned'
    )
    responsible_persons = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='tasks_assigned'
    )
    events = models.ManyToManyField(
        'events.Event',
        blank=True,
        related_name='tasks'
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    priority = models.CharField(max_length=20, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True, help_text="Optional URL to redirect when clicked")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"