from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
from accounts.models import User
from events.models import Event, Invitation
import random

class Command(BaseCommand):
    help = 'Add demo overlapping events to test Event Overlap Report feature'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding demo overlapping events...'))
        
        # Get some users - need at least 5 for good overlap scenarios
        users = list(User.objects.all()[:10])
        if len(users) < 5:
            self.stdout.write(self.style.ERROR('Need at least 5 users. Please run populate_dummy_data first.'))
            return
        
        # Get tomorrow's date (or next day) for future events
        tomorrow = timezone.now().date() + timedelta(days=1)
        now = timezone.now()
        
        # Create overlapping event scenarios
        overlaps_created = 0
        
        # Scenario 1: Same user has 2 overlapping events
        user1 = random.choice(users)
        user2 = random.choice(users)
        user3 = random.choice(users)
        
        # Create first event group - 3 users with overlapping events
        start_time1 = timezone.make_aware(datetime.combine(tomorrow, time(10, 0)))
        end_time1 = timezone.make_aware(datetime.combine(tomorrow, time(11, 30)))
        
        event1 = Event.objects.create(
            title='Team Planning Meeting',
            description='Demo overlapping event 1 - Team planning session',
            start_datetime=start_time1,
            end_datetime=end_time1,
            location='Conference Room A',
            type='MEETING',
            agenda='1. Discuss project timeline\n2. Assign tasks\n3. Q&A',
            status='UPCOMING',
            created_by=user1
        )
        
        # Add participants to event1
        participants1 = [user1, user2, user3]
        for participant in participants1:
            Invitation.objects.get_or_create(
                event=event1,
                invitee=participant,
                defaults={'status': 'ACCEPTED'}
            )
        
        # Create overlapping event (same participants, overlapping time)
        start_time2 = timezone.make_aware(datetime.combine(tomorrow, time(10, 30)))
        end_time2 = timezone.make_aware(datetime.combine(tomorrow, time(12, 0)))
        
        event2 = Event.objects.create(
            title='Client Review Session',
            description='Demo overlapping event 2 - Client review that overlaps with planning meeting',
            start_datetime=start_time2,
            end_datetime=end_time2,
            location='Conference Room B',
            type='MEETING',
            agenda='1. Review deliverables\n2. Client feedback\n3. Next steps',
            status='UPCOMING',
            created_by=user2
        )
        
        # Add same participants to create overlap
        for participant in participants1:
            Invitation.objects.get_or_create(
                event=event2,
                invitee=participant,
                defaults={'status': 'ACCEPTED'}
            )
        
        overlaps_created += 1
        self.stdout.write(f'  Created overlapping events: "{event1.title}" and "{event2.title}"')
        self.stdout.write(f'    Participants: {", ".join([u.username for u in participants1])}')
        self.stdout.write(f'    Overlap: {start_time2.strftime("%I:%M %p")} - {end_time1.strftime("%I:%M %p")}')
        
        # Scenario 2: Different overlap scenario with different users
        if len(users) >= 6:
            user4 = random.choice([u for u in users if u not in participants1])
            user5 = random.choice([u for u in users if u not in participants1])
            user6 = random.choice([u for u in users if u not in participants1])
            
            start_time3 = timezone.make_aware(datetime.combine(tomorrow, time(14, 0)))
            end_time3 = timezone.make_aware(datetime.combine(tomorrow, time(15, 30)))
            
            event3 = Event.objects.create(
                title='Code Review Session',
                description='Demo overlapping event 3 - Code review meeting',
                start_datetime=start_time3,
                end_datetime=end_time3,
                location='Virtual Meeting',
                type='MEETING',
                agenda='1. Review PRs\n2. Discuss code quality\n3. Best practices',
                status='UPCOMING',
                created_by=user4
            )
            
            participants3 = [user4, user5, user6]
            for participant in participants3:
                Invitation.objects.get_or_create(
                    event=event3,
                    invitee=participant,
                    defaults={'status': 'ACCEPTED'}
                )
            
            # Create overlapping event
            start_time4 = timezone.make_aware(datetime.combine(tomorrow, time(14, 45)))
            end_time4 = timezone.make_aware(datetime.combine(tomorrow, time(16, 15)))
            
            event4 = Event.objects.create(
                title='Sprint Retrospective',
                description='Demo overlapping event 4 - Sprint retrospective that overlaps with code review',
                start_datetime=start_time4,
                end_datetime=end_time4,
                location='Main Conference Room',
                type='MEETING',
                agenda='1. What went well\n2. Improvements\n3. Action items',
                status='UPCOMING',
                created_by=user5
            )
            
            # Add same participants
            for participant in participants3:
                Invitation.objects.get_or_create(
                    event=event4,
                    invitee=participant,
                    defaults={'status': 'ACCEPTED'}
                )
            
            overlaps_created += 1
            self.stdout.write(f'  Created overlapping events: "{event3.title}" and "{event4.title}"')
            self.stdout.write(f'    Participants: {", ".join([u.username for u in participants3])}')
            self.stdout.write(f'    Overlap: {start_time4.strftime("%I:%M %p")} - {end_time3.strftime("%I:%M %p")}')
        
        # Scenario 3: Partial overlap with some common participants
        if len(users) >= 8:
            common_user = random.choice(users)
            user7 = random.choice([u for u in users if u != common_user])
            user8 = random.choice([u for u in users if u not in [common_user, user7]])
            
            start_time5 = timezone.make_aware(datetime.combine(tomorrow, time(16, 0)))
            end_time5 = timezone.make_aware(datetime.combine(tomorrow, time(17, 0)))
            
            event5 = Event.objects.create(
                title='Training Workshop',
                description='Demo overlapping event 5 - Training session',
                start_datetime=start_time5,
                end_datetime=end_time5,
                location='Training Center',
                type='WORKSHOP',
                agenda='1. Introduction\n2. Hands-on practice\n3. Q&A',
                status='UPCOMING',
                created_by=common_user
            )
            
            participants5 = [common_user, user7, user8]
            for participant in participants5:
                Invitation.objects.get_or_create(
                    event=event5,
                    invitee=participant,
                    defaults={'status': 'ACCEPTED'}
                )
            
            # Create overlapping event with common participant
            start_time6 = timezone.make_aware(datetime.combine(tomorrow, time(16, 30)))
            end_time6 = timezone.make_aware(datetime.combine(tomorrow, time(17, 30)))
            
            event6 = Event.objects.create(
                title='Product Demo',
                description='Demo overlapping event 6 - Product demo that overlaps with training',
                start_datetime=start_time6,
                end_datetime=end_time6,
                location='Demo Room',
                type='MEETING',
                agenda='1. Feature showcase\n2. Client feedback\n3. Discussion',
                status='UPCOMING',
                created_by=common_user
            )
            
            # Add common participant + different ones
            participants6 = [common_user, user7]  # common_user and user7 overlap
            for participant in participants6:
                Invitation.objects.get_or_create(
                    event=event6,
                    invitee=participant,
                    defaults={'status': 'ACCEPTED'}
                )
            
            overlaps_created += 1
            self.stdout.write(f'  Created overlapping events: "{event5.title}" and "{event6.title}"')
            self.stdout.write(f'    Common participants: {common_user.username}, {user7.username}')
            self.stdout.write(f'    Overlap: {start_time6.strftime("%I:%M %p")} - {end_time5.strftime("%I:%M %p")}')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {overlaps_created * 2} events with {overlaps_created} overlap scenarios!'))
        self.stdout.write(self.style.SUCCESS(f'\nTo test, login as SM or PM user and visit /event-overlap-report/'))
        self.stdout.write(self.style.SUCCESS(f'\nEvents are scheduled for: {tomorrow.strftime("%B %d, %Y")}'))

