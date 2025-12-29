from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
from accounts.models import User
from core.models import Task
from events.models import Event, Invitation
import random

class Command(BaseCommand):
    help = 'Add demo events and tasks for today to test Today\'s ToDo feature'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding demo items for today...'))
        
        today = timezone.now().date()
        now = timezone.now()
        
        # Get some users
        users = list(User.objects.all()[:5])
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please run populate_dummy_data first.'))
            return
        
        # Create 3-5 events for today
        event_titles = [
            'Team Standup Meeting',
            'Client Presentation',
            'Code Review Session',
            'Project Planning Meeting',
            'Weekly Sync-up'
        ]
        
        locations = [
            'Conference Room A',
            'Main Auditorium',
            'Virtual Meeting',
            'Training Center',
            'Executive Boardroom'
        ]
        
        events_created = 0
        for i, title in enumerate(event_titles[:5]):
            # Schedule at different times today
            hour = 9 + (i * 2)  # 9am, 11am, 1pm, 3pm, 5pm
            start_time = timezone.make_aware(datetime.combine(today, time(hour, 0)))
            end_time = start_time + timedelta(hours=1)
            
            # Pick a random user as creator
            creator = random.choice(users)
            
            event = Event.objects.create(
                title=title,
                description=f'Demo event for testing Today\'s ToDo feature. This is event number {i+1}.',
                start_datetime=start_time,
                end_datetime=end_time,
                location=locations[i],
                type=random.choice([choice[0] for choice in Event.EventType.choices]),
                agenda=f'1. Agenda item one\n2. Agenda item two\n3. Discussion points',
                status='UPCOMING',
                created_by=creator
            )
            
            # Add 3-4 users as participants
            participants = random.sample(users, min(3, len(users)))
            for participant in participants:
                Invitation.objects.get_or_create(
                    event=event,
                    invitee=participant,
                    defaults={'status': 'ACCEPTED'}
                )
            
            events_created += 1
            self.stdout.write(f'  Created event: {title} at {start_time.strftime("%I:%M %p")}')
        
        # Create 3-5 tasks due today
        task_titles = [
            'Review pull requests',
            'Update project documentation',
            'Prepare meeting notes',
            'Complete daily report',
            'Respond to urgent emails'
        ]
        
        tasks_created = 0
        for i, title in enumerate(task_titles[:5]):
            # Assign to random users
            responsible_users = random.sample(users, min(2, len(users)))
            owner = random.choice(users)
            
            task = Task.objects.create(
                title=title,
                description=f'Demo task for testing Today\'s ToDo feature. This task is due today.',
                due_date=today,
                status=random.choice(['UPCOMING', 'ONGOING', 'PENDING']),
                priority=random.choice(['HIGH', 'MEDIUM', 'LOW']),
                owner=owner
            )
            
            # Add responsible persons
            task.responsible_persons.set(responsible_users)
            
            tasks_created += 1
            self.stdout.write(f'  Created task: {title} (assigned to {", ".join([u.username for u in responsible_users])})')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {events_created} events and {tasks_created} tasks for today!'))
        
        # Create specific events and tasks for SM users
        sm_users = User.objects.filter(role=User.Role.MANAGEMENT, department='Senior Management')
        if sm_users.exists():
            self.stdout.write(self.style.SUCCESS('\nAdding todos specifically for SM users...'))
            
            sm_user = sm_users.first()
            sm_event_titles = [
                'Executive Board Meeting',
                'Strategic Planning Session',
                'Quarterly Review Meeting'
            ]
            
            sm_locations = [
                'Executive Boardroom',
                'Strategic Planning Room',
                'Main Conference Hall'
            ]
            
            sm_events_created = 0
            for i, title in enumerate(sm_event_titles[:3]):
                hour = 10 + (i * 2)  # 10am, 12pm, 2pm
                start_time = timezone.make_aware(datetime.combine(today, time(hour, 0)))
                end_time = start_time + timedelta(hours=1, minutes=30)
                
                event = Event.objects.create(
                    title=title,
                    description=f'Demo event for SM user - {title}',
                    start_datetime=start_time,
                    end_datetime=end_time,
                    location=sm_locations[i],
                    type=Event.EventType.MEETING,
                    agenda=f'1. Strategic discussion\n2. Review key metrics\n3. Decision making',
                    status='UPCOMING',
                    created_by=sm_user
                )
                
                # Add SM user as participant
                Invitation.objects.get_or_create(
                    event=event,
                    invitee=sm_user,
                    defaults={'status': 'ACCEPTED'}
                )
                
                # Add a couple more users as participants
                other_users = User.objects.exclude(id=sm_user.id)[:2]
                for participant in other_users:
                    Invitation.objects.get_or_create(
                        event=event,
                        invitee=participant,
                        defaults={'status': 'ACCEPTED'}
                    )
                
                sm_events_created += 1
                self.stdout.write(f'  Created SM event: {title} at {start_time.strftime("%I:%M %p")}')
            
            # Create tasks for SM users
            sm_task_titles = [
                'Review quarterly performance reports',
                'Approve budget allocations',
                'Strategic decision review',
                'Executive dashboard analysis'
            ]
            
            sm_tasks_created = 0
            for i, title in enumerate(sm_task_titles[:4]):
                task = Task.objects.create(
                    title=title,
                    description=f'Demo task for SM user - {title}',
                    due_date=today,
                    status=random.choice(['UPCOMING', 'ONGOING', 'PENDING']),
                    priority=random.choice(['HIGH', 'MEDIUM']),
                    owner=sm_user
                )
                
                # Assign to SM user
                task.responsible_persons.add(sm_user)
                
                sm_tasks_created += 1
                self.stdout.write(f'  Created SM task: {title}')
            
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {sm_events_created} events and {sm_tasks_created} tasks for SM users!'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTo test, login as any user and visit /todays-todo/'))
        if sm_users.exists():
            self.stdout.write(self.style.SUCCESS(f'\nSM users: {", ".join([u.username for u in sm_users])}'))
        self.stdout.write(self.style.SUCCESS(f'\nSample users: {", ".join([u.username for u in users[:3]])}'))
        self.stdout.write(self.style.SUCCESS(f'Password: password123'))

