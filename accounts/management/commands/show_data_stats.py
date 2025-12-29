from django.core.management.base import BaseCommand
from accounts.models import User
from core.models import Meeting, Task
from events.models import Event, Invitation

class Command(BaseCommand):
    help = 'Display database statistics'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DATABASE STATISTICS ===\n'))
        
        # Users statistics
        total_users = User.objects.all().count()
        pm_users = User.objects.filter(role=User.Role.MANAGER, department='Project Management').count()
        sm_users = User.objects.filter(role=User.Role.MANAGEMENT, department='Senior Management').count()
        other_users = User.objects.exclude(department__in=['Project Management', 'Senior Management']).count()
        
        self.stdout.write(f'👥 USERS:')
        self.stdout.write(f'   Total Users: {total_users}')
        self.stdout.write(f'   PM (Project Management): {pm_users}')
        self.stdout.write(f'   SM (Senior Management): {sm_users}')
        self.stdout.write(f'   Other Employees: {other_users}')
        
        # Tasks statistics
        total_tasks = Task.objects.all().count()
        pending_tasks = Task.objects.filter(status=Task.StatusChoices.PENDING).count()
        in_progress_tasks = Task.objects.filter(status=Task.StatusChoices.IN_PROGRESS).count()
        completed_tasks = Task.objects.filter(status=Task.StatusChoices.COMPLETED).count()
        blocked_tasks = Task.objects.filter(status=Task.StatusChoices.BLOCKED).count()
        
        self.stdout.write(f'\n📋 TASKS:')
        self.stdout.write(f'   Total Tasks: {total_tasks}')
        self.stdout.write(f'   Pending: {pending_tasks}')
        self.stdout.write(f'   In Progress: {in_progress_tasks}')
        self.stdout.write(f'   Completed: {completed_tasks}')
        self.stdout.write(f'   Blocked: {blocked_tasks}')
        
        # Meetings statistics
        total_meetings = Meeting.objects.all().count()
        upcoming_meetings = Meeting.objects.filter(status=Meeting.MeetingStatus.UPCOMING).count()
        completed_meetings = Meeting.objects.filter(status=Meeting.MeetingStatus.COMPLETED).count()
        
        self.stdout.write(f'\n🤝 MEETINGS:')
        self.stdout.write(f'   Total Meetings: {total_meetings}')
        self.stdout.write(f'   Upcoming: {upcoming_meetings}')
        self.stdout.write(f'   Completed: {completed_meetings}')
        
        # Events statistics
        total_events = Event.objects.all().count()
        total_invitations = Invitation.objects.all().count()
        accepted_invitations = Invitation.objects.filter(status='ACCEPTED').count()
        pending_invitations = Invitation.objects.filter(status='PENDING').count()
        rejected_invitations = Invitation.objects.filter(status='REJECTED').count()
        
        self.stdout.write(f'\n🎉 EVENTS:')
        self.stdout.write(f'   Total Events: {total_events}')
        self.stdout.write(f'   Total Invitations: {total_invitations}')
        self.stdout.write(f'   Accepted: {accepted_invitations}')
        self.stdout.write(f'   Pending: {pending_invitations}')
        self.stdout.write(f'   Rejected: {rejected_invitations}')
        
        self.stdout.write(f'\n' + '='*40)
        self.stdout.write(self.style.SUCCESS('✅ Database populated successfully with dashboard-ready data!'))
        
        # Show some sample users
        self.stdout.write(f'\n📝 SAMPLE USERS:')
        pm_users_sample = User.objects.filter(department='Project Management')[:3]
        sm_users_sample = User.objects.filter(department='Senior Management')
        
        for user in pm_users_sample:
            self.stdout.write(f'   PM: {user.username} ({user.first_name} {user.last_name}) - {user.email}')
            
        for user in sm_users_sample:
            self.stdout.write(f'   SM: {user.username} ({user.first_name} {user.last_name}) - {user.email}')
            
        self.stdout.write(f'\n🔑 LOGIN CREDENTIALS:')
        self.stdout.write(f'   Username: Any of the above usernames')
        self.stdout.write(f'   Password: password123')
        self.stdout.write(f'   Admin: username=admin, password=admin (if exists)')