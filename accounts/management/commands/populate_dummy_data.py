from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import User
from core.models import Meeting, Task, Project
from events.models import Event, Invitation
from django.db import transaction
import random
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Populate database with dummy data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate dummy data...'))
        
        with transaction.atomic():
            # Clear existing data (optional)
            self.stdout.write('Clearing existing data...')
            User.objects.filter(is_superuser=False).delete()
            Project.objects.all().delete()
            Meeting.objects.all().delete()
            Task.objects.all().delete()
            Event.objects.all().delete()
            
            # Create users
            users = self.create_users()
            
            # Create projects
            projects = self.create_projects(users)
            
            # Create meetings and tasks
            meetings = self.create_meetings(users)
            
            # Create events first (needed for task linking)
            events = self.create_events(users, projects)
            
            # Create tasks (can link to events now)
            self.create_tasks(meetings, users, projects, events)
            
        self.stdout.write(self.style.SUCCESS('Successfully populated dummy data!'))

    def create_users(self):
        self.stdout.write('Creating users...')
        users = []
        
        # Create 5 PM (Project Management) users
        for i in range(5):
            user = User.objects.create_user(
                username=f'pm_user_{i+1}',
                email=f'pm{i+1}@company.com',
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=User.Role.MANAGER,
                phone_number=fake.phone_number()[:15],
                department='Project Management'
            )
            users.append(user)
            
        # Create 2 SM (Senior Management) users
        for i in range(2):
            user = User.objects.create_user(
                username=f'sm_user_{i+1}',
                email=f'sm{i+1}@company.com',
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=User.Role.MANAGEMENT,
                phone_number=fake.phone_number()[:15],
                department='Senior Management'
            )
            users.append(user)
            
        # Create additional regular users
        for i in range(8):
            user = User.objects.create_user(
                username=f'employee_{i+1}',
                email=f'emp{i+1}@company.com',
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=User.Role.MANAGER,
                phone_number=fake.phone_number()[:15],
                department=random.choice(['IT', 'Marketing', 'Sales', 'HR', 'Operations'])
            )
            users.append(user)
            
        self.stdout.write(f'Created {len(users)} users')
        return users
    
    def create_projects(self, users):
        self.stdout.write('Creating projects...')
        projects = []
        
        # Get PM users
        pm_users = [u for u in users if u.department == 'Project Management']
        
        if not pm_users:
            self.stdout.write(self.style.WARNING('No PM users found, skipping project creation'))
            return projects
        
        project_titles = [
            'Website Redesign Project',
            'Mobile App Development',
            'Data Migration Initiative',
            'Customer Portal Enhancement',
            'Security Audit & Compliance',
            'Marketing Campaign 2025',
            'Product Launch Q1',
            'Infrastructure Upgrade',
            'Training Program Development',
            'Process Automation Project'
        ]
        
        # Create 10 projects
        for i in range(min(10, len(project_titles))):
            # Assign random PM as project manager
            pm = random.choice(pm_users)
            
            # Random dates within next 180 days
            start_date = (timezone.now() + timedelta(days=random.randint(0, 30))).date()
            end_date = start_date + timedelta(days=random.randint(60, 180))
            
            project = Project.objects.create(
                title=project_titles[i],
                description=fake.text(max_nb_chars=500),
                start_date=start_date,
                end_date=end_date,
                project_manager=pm
            )
            
            # Add 3-8 random employees to project
            employees = random.sample([u for u in users if u != pm], random.randint(3, min(8, len(users)-1)))
            project.project_employees.set(employees)
            
            projects.append(project)
        
        self.stdout.write(f'Created {len(projects)} projects')
        return projects

    def create_meetings(self, users):
        self.stdout.write('Creating meetings...')
        meetings = []
        meeting_types = [choice[0] for choice in Meeting.MeetingType.choices]
        statuses = [choice[0] for choice in Meeting.MeetingStatus.choices]
        
        # Create 15 meetings (more than 10 as requested)
        for i in range(15):
            # Random date within the last 30 days or next 30 days
            days_offset = random.randint(-30, 30)
            meeting_time = timezone.now() + timedelta(days=days_offset, hours=random.randint(9, 17))
            
            meeting = Meeting.objects.create(
                title=fake.catch_phrase(),
                meeting_time=meeting_time,
                duration=random.choice([30, 60, 90, 120]),
                meeting_type=random.choice(meeting_types),
                status=Meeting.MeetingStatus.COMPLETED if days_offset < 0 else Meeting.MeetingStatus.UPCOMING
            )
            
            # Add random participants (2-6 people per meeting)
            participants = random.sample(users, random.randint(2, 6))
            meeting.participants.set(participants)
            
            meetings.append(meeting)
            
        self.stdout.write(f'Created {len(meetings)} meetings')
        return meetings

    def create_tasks(self, meetings, users, projects, events):
        self.stdout.write('Creating tasks...')
        task_count = 0
        statuses = [choice[0] for choice in Task.StatusChoices.choices]
        priorities = [choice[0] for choice in Task.PriorityChoices.choices]
        
        # Create 30 tasks
        task_titles = [
            'Review project requirements',
            'Update system documentation',
            'Conduct user testing',
            'Prepare quarterly report',
            'Fix critical bugs',
            'Design new user interface',
            'Implement security features',
            'Database optimization',
            'Client presentation preparation',
            'Team performance review',
            'Budget planning and analysis',
            'Risk assessment report',
            'Market research analysis',
            'Product roadmap update',
            'Stakeholder communication',
            'Quality assurance testing',
            'Server maintenance',
            'User training materials',
            'Compliance audit',
            'Innovation workshop planning',
            'Vendor contract negotiation',
            'Performance metrics analysis',
            'Customer feedback review',
            'Process improvement initiative',
            'Technology evaluation',
            'API Integration',
            'Frontend Development',
            'Backend Optimization',
            'Documentation Update',
            'Testing & QA'
        ]
        
        for i in range(min(30, len(task_titles))):
            # Random due date within next 60 days
            due_date = (timezone.now() + timedelta(days=random.randint(1, 60))).date()
            
            # 70% chance task belongs to a project
            project = random.choice(projects) if projects and random.random() < 0.7 else None
            
            # Get project employees if task has project
            responsible_users = []
            if project:
                responsible_users = list(project.project_employees.all()[:random.randint(1, 3)])
            else:
                responsible_users = [random.choice(users)]
            
            task = Task.objects.create(
                title=task_titles[i],
                description=fake.text(max_nb_chars=200),
                meeting=random.choice(meetings) if random.random() < 0.5 else None,
                project=project,
                owner=random.choice(users),
                due_date=due_date,
                status=random.choice(statuses),
                priority=random.choice(priorities)
            )
            
            # Add responsible persons
            if responsible_users:
                task.responsible_persons.set(responsible_users)
            
            # Link to events (30% chance)
            if events and random.random() < 0.3:
                task.events.set(random.sample(events, random.randint(1, min(2, len(events)))))
            
            task_count += 1
            
        self.stdout.write(f'Created {task_count} tasks')

    def create_events(self, users, projects):
        self.stdout.write('Creating events...')
        events = []
        
        event_titles = [
            'Annual Company Meeting',
            'Product Launch Event',
            'Team Building Workshop',
            'Quarterly Business Review',
            'Technology Conference',
            'Client Appreciation Dinner',
            'Training and Development Session',
            'Industry Networking Event',
            'Project Kick-off Meeting',
            'Board of Directors Meeting',
            'Employee Recognition Ceremony',
            'Innovation Summit',
            'Customer Success Workshop',
            'Strategic Planning Retreat',
            'Holiday Party',
            'Security Training Session',
            'Agile Methodology Workshop',
            'Database Architecture Review',
            'UX Design Workshop',
            'Code Review Session'
        ]
        
        locations = [
            'Conference Room A',
            'Main Auditorium',
            'Training Center',
            'Executive Boardroom',
            'Hotel Grand Ballroom',
            'Company Headquarters',
            'Innovation Lab',
            'Client Office',
            'Convention Center',
            'Virtual Meeting',
            'Outdoor Venue',
            'Restaurant Private Room'
        ]
        
        event_types = [choice[0] for choice in Event.EventType.choices]
        event_statuses = [choice[0] for choice in Event.EventStatus.choices]
        
        # Create 20 events
        for i in range(min(20, len(event_titles))):
            # Random date within the last 15 days or next 45 days
            days_offset = random.randint(-15, 45)
            start_time = timezone.now() + timedelta(
                days=days_offset, 
                hours=random.randint(9, 16),
                minutes=random.choice([0, 15, 30, 45])
            )
            end_time = start_time + timedelta(hours=random.randint(1, 4))
            
            # Determine status based on date
            if days_offset < 0:
                status = Event.EventStatus.COMPLETED
            elif days_offset > 30:
                status = Event.EventStatus.UPCOMING
            else:
                status = random.choice([Event.EventStatus.UPCOMING, Event.EventStatus.COMPLETED])
            
            # Get project employees if event is project-related
            participants = []
            if projects and random.random() < 0.6:
                # Link to project employees
                project = random.choice(projects)
                participants = list(project.project_employees.all()[:random.randint(3, 8)])
            else:
                # Random participants
                participants = random.sample(users, random.randint(3, 8))
            
            # Get creator (PM or SM preferred for project events)
            creator = random.choice(users)
            if projects and random.random() < 0.5:
                pm_users = [u for u in users if u.department == 'Project Management']
                if pm_users:
                    creator = random.choice(pm_users)
            
            event = Event.objects.create(
                title=event_titles[i],
                description=fake.text(max_nb_chars=300),
                start_datetime=start_time,
                end_datetime=end_time,
                location=random.choice(locations),
                type=random.choice(event_types),
                agenda=fake.text(max_nb_chars=200) if random.random() < 0.7 else None,
                status=status,
                created_by=creator
            )
            
            # Add participants via Invitation
            for participant in participants:
                invitation_status = random.choice(['PENDING', 'ACCEPTED', 'REJECTED'])
                Invitation.objects.create(
                    event=event,
                    invitee=participant,
                    status=invitation_status
                )
            
            events.append(event)
            
        self.stdout.write(f'Created {len(events)} events')
        return events

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-data',
            action='store_true',
            help='Clear existing data before creating new dummy data',
        )