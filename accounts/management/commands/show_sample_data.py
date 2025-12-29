from django.core.management.base import BaseCommand
from accounts.models import User
from core.models import Meeting, Task
from events.models import Event
from django.utils import timezone

class Command(BaseCommand):
    help = 'Display sample data from the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== SAMPLE DATABASE CONTENT ===\n'))
        
        # Sample Tasks
        self.stdout.write(self.style.WARNING('📋 RECENT TASKS:'))
        tasks = Task.objects.all().order_by('-created_at')[:10]
        for i, task in enumerate(tasks, 1):
            status_color = {
                'PENDING': self.style.WARNING,
                'IN_PROGRESS': self.style.HTTP_INFO,
                'COMPLETED': self.style.SUCCESS,
                'BLOCKED': self.style.ERROR
            }.get(task.status, self.style.NOTICE)
            
            self.stdout.write(f'{i:2d}. {task.title[:40]:<40} | {status_color(task.status)} | {task.priority} | Due: {task.due_date}')
        
        # Sample Meetings  
        self.stdout.write(f'\n{self.style.WARNING("🤝 UPCOMING MEETINGS:")}')
        meetings = Meeting.objects.filter(meeting_time__gte=timezone.now()).order_by('meeting_time')[:8]
        for i, meeting in enumerate(meetings, 1):
            participants_count = meeting.participants.count()
            meeting_date = meeting.meeting_time.strftime('%b %d, %Y at %I:%M %p')
            self.stdout.write(f'{i:2d}. {meeting.title[:35]:<35} | {meeting.meeting_type} | {meeting_date} | {participants_count} participants')
        
        # Sample Events
        self.stdout.write(f'\n{self.style.WARNING("🎉 UPCOMING EVENTS:")}')
        events = Event.objects.filter(start_datetime__gte=timezone.now()).order_by('start_datetime')[:8]
        for i, event in enumerate(events, 1):
            event_date = event.start_datetime.strftime('%b %d, %Y at %I:%M %p')
            participants_count = event.participants.count()
            self.stdout.write(f'{i:2d}. {event.title[:35]:<35} | {event.location[:20]:<20} | {event_date} | {participants_count} participants')
        
        # Users by Role
        self.stdout.write(f'\n{self.style.WARNING("👥 USERS BY DEPARTMENT:")}')
        
        self.stdout.write(f'   {self.style.SUCCESS("Senior Management (SM):")}')
        sm_users = User.objects.filter(department='Senior Management')
        for user in sm_users:
            self.stdout.write(f'      • {user.first_name} {user.last_name} ({user.username}) - {user.email}')
        
        self.stdout.write(f'   {self.style.HTTP_INFO("Project Management (PM):")}')
        pm_users = User.objects.filter(department='Project Management')
        for user in pm_users:
            self.stdout.write(f'      • {user.first_name} {user.last_name} ({user.username}) - {user.email}')
            
        self.stdout.write(f'\n{self.style.SUCCESS("✅ All data is ready for dashboard visualization!")}')