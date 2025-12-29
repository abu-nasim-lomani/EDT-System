from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
from accounts.models import User
from core.models import Task
from events.models import Event, Invitation
import random

class Command(BaseCommand):
    help = 'Add demo todos and overlap events specifically for SM and PM users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding demo todos and overlap events for SM and PM users...'))
        
        # Get SM users (Management role, Senior Management department)
        sm_users = User.objects.filter(role=User.Role.MANAGEMENT, department='Senior Management')
        
        # Get PM users (Manager role, Project Management department)
        pm_users = User.objects.filter(role=User.Role.MANAGER, department='Project Management')
        
        if not sm_users.exists():
            self.stdout.write(self.style.WARNING('No SM users found. Creating one...'))
            sm_user = User.objects.create_user(
                username='sm_demo',
                email='sm@company.com',
                password='password123',
                first_name='Senior',
                last_name='Manager',
                role=User.Role.MANAGEMENT,
                department='Senior Management'
            )
            sm_users = User.objects.filter(id=sm_user.id)
            self.stdout.write(self.style.SUCCESS(f'Created SM user: {sm_user.username}'))
        
        if not pm_users.exists():
            self.stdout.write(self.style.WARNING('No PM users found. Creating one...'))
            pm_user = User.objects.create_user(
                username='pm_demo',
                email='pm@company.com',
                password='password123',
                first_name='Project',
                last_name='Manager',
                role=User.Role.MANAGER,
                department='Project Management'
            )
            pm_users = User.objects.filter(id=pm_user.id)
            self.stdout.write(self.style.SUCCESS(f'Created PM user: {pm_user.username}'))
        
        sm_user = sm_users.first()
        pm_user = pm_users.first()
        
        # Get other users for participants
        other_users = list(User.objects.exclude(id__in=[sm_user.id, pm_user.id])[:5])
        if len(other_users) < 2:
            self.stdout.write(self.style.WARNING('Not enough users for participants. Using SM and PM users as participants.'))
            other_users = [sm_user, pm_user]
        
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # ========== CREATE DEMO TODOS FOR SM USER ==========
        self.stdout.write(self.style.SUCCESS('\n=== Creating demo todos for SM user ==='))
        
        sm_task_titles = [
            'Review quarterly performance reports',
            'Approve budget allocations for Q2',
            'Strategic decision review meeting prep',
            'Executive dashboard analysis',
            'Board meeting preparation',
            'Review department KPIs',
            'Approve new project proposals',
            'Strategic planning document review'
        ]
        
        sm_tasks_created = 0
        for i, title in enumerate(sm_task_titles[:6]):
            due_date = today + timedelta(days=random.randint(0, 3))
            task = Task.objects.create(
                title=title,
                description=f'Demo task for SM user - {title}. This requires strategic oversight and decision making.',
                due_date=due_date,
                status=random.choice(['UPCOMING', 'ONGOING', 'PENDING']),
                priority=random.choice(['HIGH', 'MEDIUM']),
                owner=sm_user
            )
            
            # Assign to SM user
            task.responsible_persons.add(sm_user)
            
            # Sometimes add PM user as collaborator
            if i % 2 == 0 and pm_user:
                task.responsible_persons.add(pm_user)
            
            sm_tasks_created += 1
            self.stdout.write(f'  ✓ Created SM task: {title} (due: {due_date.strftime("%b %d")})')
        
        # ========== CREATE DEMO TODOS FOR PM USER ==========
        self.stdout.write(self.style.SUCCESS('\n=== Creating demo todos for PM user ==='))
        
        pm_task_titles = [
            'Update project timeline and milestones',
            'Review team sprint progress',
            'Prepare project status report',
            'Coordinate with stakeholders',
            'Resource allocation planning',
            'Risk assessment documentation',
            'Team performance review',
            'Project budget tracking'
        ]
        
        pm_tasks_created = 0
        for i, title in enumerate(pm_task_titles[:6]):
            due_date = today + timedelta(days=random.randint(0, 3))
            task = Task.objects.create(
                title=title,
                description=f'Demo task for PM user - {title}. This requires project management expertise.',
                due_date=due_date,
                status=random.choice(['UPCOMING', 'ONGOING', 'PENDING']),
                priority=random.choice(['HIGH', 'MEDIUM', 'LOW']),
                owner=pm_user
            )
            
            # Assign to PM user
            task.responsible_persons.add(pm_user)
            
            # Sometimes add team members
            if len(other_users) > 0:
                team_members = random.sample(other_users, min(2, len(other_users)))
                for member in team_members:
                    task.responsible_persons.add(member)
            
            pm_tasks_created += 1
            self.stdout.write(f'  ✓ Created PM task: {title} (due: {due_date.strftime("%b %d")})')
        
        # ========== CREATE OVERLAP EVENTS FOR SM AND PM USERS ==========
        self.stdout.write(self.style.SUCCESS('\n=== Creating overlap events for SM and PM users ==='))
        
        overlaps_created = 0
        
        # Scenario 1: SM and PM both have overlapping events
        start_time1 = timezone.make_aware(datetime.combine(tomorrow, time(10, 0)))
        end_time1 = timezone.make_aware(datetime.combine(tomorrow, time(11, 30)))
        
        event1 = Event.objects.create(
            title='Executive Strategy Meeting',
            description='Demo overlap event 1 - Strategic planning session involving SM and PM',
            start_datetime=start_time1,
            end_datetime=end_time1,
            location='Executive Boardroom',
            type='MEETING',
            agenda='1. Strategic objectives\n2. Resource planning\n3. Q&A session',
            status='UPCOMING',
            created_by=sm_user
        )
        
        # Add SM, PM, and other participants
        participants1 = [sm_user, pm_user] + other_users[:2]
        for participant in participants1:
            Invitation.objects.get_or_create(
                event=event1,
                invitee=participant,
                defaults={'status': 'ACCEPTED'}
            )
        
        # Create overlapping event (SM and PM both invited)
        start_time2 = timezone.make_aware(datetime.combine(tomorrow, time(10, 30)))
        end_time2 = timezone.make_aware(datetime.combine(tomorrow, time(12, 0)))
        
        event2 = Event.objects.create(
            title='Project Review with Management',
            description='Demo overlap event 2 - Project review that overlaps with strategy meeting',
            start_datetime=start_time2,
            end_datetime=end_time2,
            location='Conference Room A',
            type='MEETING',
            agenda='1. Project status update\n2. Budget review\n3. Timeline discussion',
            status='UPCOMING',
            created_by=pm_user
        )
        
        # Add same SM and PM to create overlap
        participants2 = [sm_user, pm_user] + other_users[:1]
        for participant in participants2:
            Invitation.objects.get_or_create(
                event=event2,
                invitee=participant,
                defaults={'status': 'ACCEPTED'}
            )
        
        overlaps_created += 1
        self.stdout.write(f'  ✓ Created overlapping events: "{event1.title}" and "{event2.title}"')
        self.stdout.write(f'    SM & PM both invited - Overlap: {start_time2.strftime("%I:%M %p")} - {end_time1.strftime("%I:%M %p")}')
        
        # Scenario 2: PM has overlapping events with different participants
        if len(other_users) >= 2:
            start_time3 = timezone.make_aware(datetime.combine(tomorrow, time(14, 0)))
            end_time3 = timezone.make_aware(datetime.combine(tomorrow, time(15, 30)))
            
            event3 = Event.objects.create(
                title='Sprint Planning Session',
                description='Demo overlap event 3 - Sprint planning meeting',
                start_datetime=start_time3,
                end_datetime=end_time3,
                location='Project Room',
                type='MEETING',
                agenda='1. Sprint goals\n2. Task assignment\n3. Timeline review',
                status='UPCOMING',
                created_by=pm_user
            )
            
            participants3 = [pm_user] + other_users[:3]
            for participant in participants3:
                Invitation.objects.get_or_create(
                    event=event3,
                    invitee=participant,
                    defaults={'status': 'ACCEPTED'}
                )
            
            # Create overlapping event for PM
            start_time4 = timezone.make_aware(datetime.combine(tomorrow, time(14, 45)))
            end_time4 = timezone.make_aware(datetime.combine(tomorrow, time(16, 15)))
            
            event4 = Event.objects.create(
                title='Client Stakeholder Meeting',
                description='Demo overlap event 4 - Client meeting that overlaps with sprint planning',
                start_datetime=start_time4,
                end_datetime=end_time4,
                location='Virtual Meeting',
                type='MEETING',
                agenda='1. Project update\n2. Client feedback\n3. Next steps',
                status='UPCOMING',
                created_by=pm_user
            )
            
            # PM user overlaps
            participants4 = [pm_user] + other_users[:2]
            for participant in participants4:
                Invitation.objects.get_or_create(
                    event=event4,
                    invitee=participant,
                    defaults={'status': 'ACCEPTED'}
                )
            
            overlaps_created += 1
            self.stdout.write(f'  ✓ Created overlapping events: "{event3.title}" and "{event4.title}"')
            self.stdout.write(f'    PM user has overlap - Overlap: {start_time4.strftime("%I:%M %p")} - {end_time3.strftime("%I:%M %p")}')
        
        # Scenario 3: SM has overlapping events
        if len(other_users) >= 2:
            start_time5 = timezone.make_aware(datetime.combine(tomorrow, time(16, 0)))
            end_time5 = timezone.make_aware(datetime.combine(tomorrow, time(17, 0)))
            
            event5 = Event.objects.create(
                title='Board Meeting Preparation',
                description='Demo overlap event 5 - Board meeting prep session',
                start_datetime=start_time5,
                end_datetime=end_time5,
                location='Executive Office',
                type='MEETING',
                agenda='1. Review materials\n2. Prepare presentation\n3. Discussion points',
                status='UPCOMING',
                created_by=sm_user
            )
            
            participants5 = [sm_user] + other_users[:2]
            for participant in participants5:
                Invitation.objects.get_or_create(
                    event=event5,
                    invitee=participant,
                    defaults={'status': 'ACCEPTED'}
                )
            
            # Create overlapping event for SM
            start_time6 = timezone.make_aware(datetime.combine(tomorrow, time(16, 30)))
            end_time6 = timezone.make_aware(datetime.combine(tomorrow, time(17, 30)))
            
            event6 = Event.objects.create(
                title='Quarterly Review Discussion',
                description='Demo overlap event 6 - Quarterly review that overlaps with board prep',
                start_datetime=start_time6,
                end_datetime=end_time6,
                location='Conference Room B',
                type='MEETING',
                agenda='1. Q1 performance\n2. Key metrics\n3. Action items',
                status='UPCOMING',
                created_by=sm_user
            )
            
            # SM user overlaps
            participants6 = [sm_user, pm_user] + other_users[:1]
            for participant in participants6:
                Invitation.objects.get_or_create(
                    event=event6,
                    invitee=participant,
                    defaults={'status': 'ACCEPTED'}
                )
            
            overlaps_created += 1
            self.stdout.write(f'  ✓ Created overlapping events: "{event5.title}" and "{event6.title}"')
            self.stdout.write(f'    SM user has overlap - Overlap: {start_time6.strftime("%I:%M %p")} - {end_time5.strftime("%I:%M %p")}')
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n=== Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {sm_tasks_created} todos for SM user ({sm_user.username})'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {pm_tasks_created} todos for PM user ({pm_user.username})'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {overlaps_created * 2} events with {overlaps_created} overlap scenarios'))
        self.stdout.write(self.style.SUCCESS(f'\nEvents are scheduled for: {tomorrow.strftime("%B %d, %Y")}'))
        self.stdout.write(self.style.SUCCESS(f'\nTo test:'))
        self.stdout.write(self.style.SUCCESS(f'  - Login as SM user: {sm_user.username} (password: password123)'))
        self.stdout.write(self.style.SUCCESS(f'  - Login as PM user: {pm_user.username} (password: password123)'))
        self.stdout.write(self.style.SUCCESS(f'  - Visit /todays-todo/ to see todos'))
        self.stdout.write(self.style.SUCCESS(f'  - Visit /event-overlap-report/ to see overlap events'))


