# chatbot/command_handler.py

import re
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from core.models import Project, Task, Meeting
from events.models import Event
from accounts.models import User
from core.utils import is_pm_user, is_sm_user, log_change
from .response_handler import get_rule_based_response


class CommandHandler:
    """Handles natural language commands for CRUD operations"""
    
    def __init__(self, user, user_context):
        self.user = user
        self.user_context = user_context
        self.is_pm = is_pm_user(user)
        self.is_sm = is_sm_user(user)
    
    def parse_command(self, message):
        """Parse natural language command and return action type and parameters"""
        message_lower = message.lower().strip()
        
        # Navigation commands (check first before other commands)
        # Check for "my task" or "my tasks" patterns first
        if re.search(r'\b(go\s+to|navigate\s+to|open|show|view|take\s+me\s+to)\s+my\s+task', message_lower):
            return {'action': 'navigate', 'route': 'my_tasks'}
        
        nav_patterns = [
            (r'\b(go\s+to|navigate\s+to|open|show|view|take\s+me\s+to)\s+my\s+tasks?\b', 'my_tasks'),
            (r'\b(go\s+to|navigate\s+to|open|show|view|take\s+me\s+to)\s+all\s+tasks?\b', 'task_list'),
            (r'\b(go\s+to|navigate\s+to|open|show|view|take\s+me\s+to)\s+my\s+projects?\b', 'project_list'),
            (r'\b(go\s+to|navigate\s+to|open|show|view|take\s+me\s+to)\s+my\s+events?\b', 'my_events'),
            (r'\b(go\s+to|navigate\s+to|open|show|view|take\s+me\s+to)\s+all\s+events?\b', 'event_list'),
            (r'\b(go\s+to|navigate\s+to|open|show|view|take\s+me\s+to)\s+my\s+meetings?\b', 'meeting_list'),
            (r'\b(go\s+to|navigate\s+to|open|show|view|take\s+me\s+to)\s+dashboard\b', 'dashboard'),
            (r'\b(go\s+to|navigate\s+to|open|show|view|take\s+me\s+to)\s+pm\s+dashboard\b', 'pm_dashboard'),
            (r'\b(go\s+to|navigate\s+to|open|show|view|take\s+me\s+to)\s+management\s+dashboard\b', 'management_dashboard'),
            (r'\b(go\s+to|navigate\s+to|open|show|view|take\s+me\s+to)\s+today\'?s?\s+todo\b', 'todays_todo'),
        ]
        
        for pattern, route_name in nav_patterns:
            if re.search(pattern, message_lower):
                return {'action': 'navigate', 'route': route_name}
        
        # Create commands
        if re.search(r'\b(create|add|new|make)\s+(project|task|event|meeting)', message_lower):
            return self._parse_create_command(message, message_lower)
        
        # Update commands
        if re.search(r'\b(update|change|modify|edit|set|mark)\s+(project|task|event|meeting)', message_lower):
            return self._parse_update_command(message, message_lower)
        
        # Delete commands
        if re.search(r'\b(delete|remove|cancel)\s+(project|task|event|meeting)', message_lower):
            return self._parse_delete_command(message, message_lower)
        
        # Status change commands
        if re.search(r'\b(complete|finish|done|close|start|begin|hold|pause)\s+(task|project|event|meeting)', message_lower):
            return self._parse_status_command(message, message_lower)
        
        return None
    
    def _parse_create_command(self, message, message_lower):
        """Parse create command"""
        # Extract entity type
        entity_type = None
        for etype in ['project', 'task', 'event', 'meeting']:
            if etype in message_lower:
                entity_type = etype
                break
        
        if not entity_type:
            return None
        
        params = {'action': 'create', 'entity_type': entity_type}
        
        # Extract title (usually after "create/add/new [entity]")
        title_match = re.search(rf'(?:create|add|new|make)\s+{entity_type}\s+["\']?([^"\']+?)(?:\s+(?:with|for|on|at|by|to|due|on|date|time)|$)', message_lower)
        if not title_match:
            # Try to extract title from quoted text
            title_match = re.search(r'["\']([^"\']+)["\']', message)
            if title_match:
                params['title'] = title_match.group(1)
            else:
                # Try to extract after entity type
                parts = message.split(entity_type, 1)
                if len(parts) > 1:
                    title = parts[1].strip()
                    # Remove common words and date/time patterns
                    title = re.sub(r'^(with|for|on|at|by|to|due|date|time)\s+', '', title, flags=re.IGNORECASE)
                    # Remove date patterns
                    title = re.sub(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', '', title)
                    # Remove time patterns
                    title = re.sub(r'\d{1,2}:\d{2}\s*(am|pm)?', '', title, flags=re.IGNORECASE)
                    title = title.strip()
                    if title and len(title) > 3:
                        params['title'] = title[:200]
        else:
            title = title_match.group(1).strip()
            # Clean up title
            title = re.sub(r'\s+(?:with|for|on|at|by|to|due|date|time).*$', '', title, flags=re.IGNORECASE)
            params['title'] = title[:200]
        
        # Extract dates
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # MM/DD/YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD
            r'(today|tomorrow|next week|next month)',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message_lower)
            if match:
                params['date'] = self._parse_date(match.group(0))
                break
        
        # Extract time
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', message_lower)
        if time_match:
            params['time'] = time_match.group(0)
        
        # Extract priority
        if 'high' in message_lower and 'priority' in message_lower:
            params['priority'] = 'HIGH'
        elif 'low' in message_lower and 'priority' in message_lower:
            params['priority'] = 'LOW'
        elif 'medium' in message_lower and 'priority' in message_lower:
            params['priority'] = 'MEDIUM'
        
        # Extract project reference
        projects = self.user_context.get('projects', [])
        for project in projects:
            if project['title'].lower() in message_lower:
                params['project_id'] = project['id']
                break
        
        # Extract user mentions
        users = User.objects.all()
        for user_obj in users:
            if user_obj.username.lower() in message_lower or user_obj.get_full_name().lower() in message_lower:
                if 'assign' not in params:
                    params['assign'] = []
                params['assign'].append(user_obj.id)
        
        return params
    
    def _parse_update_command(self, message, message_lower):
        """Parse update command"""
        # Extract entity type
        entity_type = None
        for etype in ['project', 'task', 'event', 'meeting']:
            if etype in message_lower:
                entity_type = etype
                break
        
        if not entity_type:
            return None
        
        params = {'action': 'update', 'entity_type': entity_type}
        
        # Extract ID or title
        id_match = re.search(rf'{entity_type}\s*(?:#|id)?\s*(\d+)', message_lower)
        if id_match:
            params['id'] = int(id_match.group(1))
        else:
            # Try to find by title
            entities = self._get_entities_by_type(entity_type)
            for entity in entities:
                if entity.get('title', '').lower() in message_lower:
                    params['id'] = entity['id']
                    break
        
        # Extract fields to update
        if 'status' in message_lower:
            if 'complete' in message_lower or 'done' in message_lower:
                params['status'] = 'COMPLETED'
            elif 'pending' in message_lower:
                params['status'] = 'PENDING'
            elif 'ongoing' in message_lower:
                params['status'] = 'ONGOING'
        
        if 'priority' in message_lower:
            if 'high' in message_lower:
                params['priority'] = 'HIGH'
            elif 'low' in message_lower:
                params['priority'] = 'LOW'
            elif 'medium' in message_lower:
                params['priority'] = 'MEDIUM'
        
        # Extract date updates
        date_match = re.search(r'due\s+(?:on|date)?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', message_lower)
        if date_match:
            params['due_date'] = self._parse_date(date_match.group(1))
        
        return params
    
    def _parse_delete_command(self, message, message_lower):
        """Parse delete command"""
        entity_type = None
        for etype in ['project', 'task', 'event', 'meeting']:
            if etype in message_lower:
                entity_type = etype
                break
        
        if not entity_type:
            return None
        
        params = {'action': 'delete', 'entity_type': entity_type}
        
        # Extract ID or title
        id_match = re.search(rf'{entity_type}\s*(?:#|id)?\s*(\d+)', message_lower)
        if id_match:
            params['id'] = int(id_match.group(1))
        else:
            entities = self._get_entities_by_type(entity_type)
            for entity in entities:
                if entity.get('title', '').lower() in message_lower:
                    params['id'] = entity['id']
                    break
        
        return params
    
    def _parse_status_command(self, message, message_lower):
        """Parse status change command"""
        entity_type = None
        for etype in ['project', 'task', 'event', 'meeting']:
            if etype in message_lower:
                entity_type = etype
                break
        
        if not entity_type:
            return None
        
        params = {'action': 'update', 'entity_type': entity_type}
        
        # Determine status
        if 'complete' in message_lower or 'finish' in message_lower or 'done' in message_lower:
            params['status'] = 'COMPLETED'
        elif 'start' in message_lower or 'begin' in message_lower:
            params['status'] = 'ONGOING'
        elif 'hold' in message_lower or 'pause' in message_lower:
            params['status'] = 'HOLDING'
        elif 'pending' in message_lower:
            params['status'] = 'PENDING'
        
        # Extract ID or title
        id_match = re.search(rf'{entity_type}\s*(?:#|id)?\s*(\d+)', message_lower)
        if id_match:
            params['id'] = int(id_match.group(1))
        else:
            entities = self._get_entities_by_type(entity_type)
            for entity in entities:
                if entity.get('title', '').lower() in message_lower:
                    params['id'] = entity['id']
                    break
        
        return params
    
    def _parse_date(self, date_str):
        """Parse date string to date object"""
        if not date_str:
            return None
            
        date_str = date_str.lower().strip()
        
        # Handle relative dates
        if date_str == 'today':
            return timezone.now().date()
        elif date_str == 'tomorrow':
            return (timezone.now() + timedelta(days=1)).date()
        elif date_str == 'next week':
            return (timezone.now() + timedelta(days=7)).date()
        elif date_str == 'next month':
            return (timezone.now() + timedelta(days=30)).date()
        
        # Try to parse date formats
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%m-%d-%Y', '%d-%m-%Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except:
                continue
        
        # Try to parse dates like "January 15, 2024" or "Jan 15"
        try:
            # Try common date formats using dateutil if available
            try:
                from dateutil import parser
                return parser.parse(date_str).date()
            except ImportError:
                pass
        except:
            pass
        
        return None
    
    def _get_entities_by_type(self, entity_type):
        """Get entities of a specific type from context"""
        if entity_type == 'project':
            return self.user_context.get('projects', [])
        elif entity_type == 'task':
            return self.user_context.get('tasks', [])
        elif entity_type == 'event':
            return self.user_context.get('events', [])
        return []
    
    def execute_command(self, command_params):
        """Execute the parsed command"""
        action = command_params.get('action')
        entity_type = command_params.get('entity_type')
        
        try:
            if action == 'navigate':
                return self._navigate_to_page(command_params)
            elif action == 'create':
                return self._create_entity(command_params)
            elif action == 'update':
                return self._update_entity(command_params)
            elif action == 'delete':
                return self._delete_entity(command_params)
        except Exception as e:
            return {'success': False, 'message': f'Error executing command: {str(e)}'}
    
    def _navigate_to_page(self, params):
        """Handle navigation commands"""
        from django.urls import reverse
        
        route = params.get('route')
        
        # Map route names to URL names
        route_map = {
            'my_tasks': 'my_tasks',
            'task_list': 'task_list',
            'project_list': 'project_list',
            'my_events': 'my_events',
            'event_list': 'event_list',
            'meeting_list': 'meeting_list',
            'dashboard': 'home',
            'pm_dashboard': 'pm_dashboard',
            'management_dashboard': 'management_dashboard',
            'todays_todo': 'todays_todo',
        }
        
        url_name = route_map.get(route)
        if not url_name:
            return {'success': False, 'message': f'Unknown navigation route: {route}'}
        
        try:
            url = reverse(url_name)
            return {
                'success': True,
                'message': f'Navigating to {route.replace("_", " ").title()}...',
                'navigate': True,
                'url': url
            }
        except Exception as e:
            return {'success': False, 'message': f'Error generating navigation URL: {str(e)}'}
    
    def _create_entity(self, params):
        """Create a new entity"""
        entity_type = params.get('entity_type')
        title = params.get('title')
        
        if not title:
            return {'success': False, 'message': f'Please provide a title for the {entity_type}.'}
        
        if entity_type == 'project':
            return self._create_project(params)
        elif entity_type == 'task':
            return self._create_task(params)
        elif entity_type == 'event':
            return self._create_event(params)
        elif entity_type == 'meeting':
            return self._create_meeting(params)
        
        return {'success': False, 'message': f'Unknown entity type: {entity_type}'}
    
    def _create_project(self, params):
        """Create a new project"""
        if not (self.is_pm or self.is_sm):
            return {'success': False, 'message': 'You do not have permission to create projects.'}
        
        title = params.get('title')
        start_date = params.get('date') or timezone.now().date()
        end_date = params.get('date') or (timezone.now() + timedelta(days=30)).date()
        
        project = Project.objects.create(
            title=title[:200],
            description=params.get('description', ''),
            start_date=start_date,
            end_date=end_date,
            project_manager=self.user if self.is_pm else None
        )
        
        # Assign users if specified
        if params.get('assign'):
            project.project_employees.set(params['assign'])
        
        log_change('PROJECT', project.id, 'CREATE', self.user, {'title': title})
        
        return {
            'success': True,
            'message': f'Project "{title}" created successfully (ID: {project.id}).',
            'entity_id': project.id,
            'entity_type': 'project'
        }
    
    def _create_task(self, params):
        """Create a new task"""
        title = params.get('title')
        project_id = params.get('project_id')
        
        # Get project
        project = None
        if project_id:
            try:
                if self.is_sm:
                    project = Project.objects.get(id=project_id)
                elif self.is_pm:
                    project = Project.objects.get(id=project_id, project_manager=self.user)
                else:
                    project = Project.objects.get(id=project_id, project_employees=self.user)
            except Project.DoesNotExist:
                pass
        
        # If no project specified, use first available project
        if not project:
            projects = self.user_context.get('projects', [])
            if projects:
                try:
                    project = Project.objects.get(id=projects[0]['id'])
                except:
                    pass
        
        task = Task.objects.create(
            title=title[:255],
            description=params.get('description', ''),
            project=project,
            due_date=params.get('date'),
            priority=params.get('priority', 'MEDIUM'),
            owner=self.user
        )
        
        # Assign users
        assign_ids = params.get('assign', [])
        if assign_ids:
            task.responsible_persons.set(assign_ids)
        else:
            task.responsible_persons.add(self.user)
        
        log_change('TASK', task.id, 'CREATE', self.user, {'title': title})
        
        return {
            'success': True,
            'message': f'Task "{title}" created successfully (ID: {task.id}).',
            'entity_id': task.id,
            'entity_type': 'task'
        }
    
    def _create_event(self, params):
        """Create a new event"""
        if not (self.is_pm or self.is_sm):
            return {'success': False, 'message': 'You do not have permission to create events.'}
        
        title = params.get('title')
        start_datetime = timezone.now()
        
        # Parse date and time
        if params.get('date'):
            date = params.get('date')
            if params.get('time'):
                # Parse time string
                time_str = params.get('time')
                try:
                    time_obj = datetime.strptime(time_str, '%I:%M %p').time()
                except:
                    try:
                        time_obj = datetime.strptime(time_str, '%H:%M').time()
                    except:
                        time_obj = timezone.now().time()
                start_datetime = datetime.combine(date, time_obj)
            else:
                start_datetime = datetime.combine(date, timezone.now().time())
        
        event = Event.objects.create(
            title=title[:200],
            description=params.get('description', ''),
            start_datetime=start_datetime,
            type=params.get('type', 'MEETING'),
            created_by=self.user
        )
        
        # Add participants
        assign_ids = params.get('assign', [])
        if assign_ids:
            event.participants.set(assign_ids)
        event.participants.add(self.user)
        
        log_change('EVENT', event.id, 'CREATE', self.user, {'title': title})
        
        return {
            'success': True,
            'message': f'Event "{title}" created successfully (ID: {event.id}).',
            'entity_id': event.id,
            'entity_type': 'event'
        }
    
    def _create_meeting(self, params):
        """Create a new meeting"""
        title = params.get('title')
        meeting_time = timezone.now()
        
        # Parse date and time
        if params.get('date'):
            date = params.get('date')
            if params.get('time'):
                time_str = params.get('time')
                try:
                    time_obj = datetime.strptime(time_str, '%I:%M %p').time()
                except:
                    try:
                        time_obj = datetime.strptime(time_str, '%H:%M').time()
                    except:
                        time_obj = timezone.now().time()
                meeting_time = datetime.combine(date, time_obj)
            else:
                meeting_time = datetime.combine(date, timezone.now().time())
        
        meeting = Meeting.objects.create(
            title=title[:200],
            meeting_time=meeting_time,
            duration=params.get('duration', 60),
            meeting_type=params.get('meeting_type', 'TEAM')
        )
        
        # Add participants
        assign_ids = params.get('assign', [])
        if assign_ids:
            meeting.participants.set(assign_ids)
        meeting.participants.add(self.user)
        
        return {
            'success': True,
            'message': f'Meeting "{title}" created successfully (ID: {meeting.id}).',
            'entity_id': meeting.id,
            'entity_type': 'meeting'
        }
    
    def _update_entity(self, params):
        """Update an existing entity"""
        entity_type = params.get('entity_type')
        entity_id = params.get('id')
        
        if not entity_id:
            return {'success': False, 'message': f'Please specify which {entity_type} to update (use ID or title).'}
        
        if entity_type == 'project':
            return self._update_project(params)
        elif entity_type == 'task':
            return self._update_task(params)
        elif entity_type == 'event':
            return self._update_event(params)
        elif entity_type == 'meeting':
            return self._update_meeting(params)
        
        return {'success': False, 'message': f'Unknown entity type: {entity_type}'}
    
    def _update_project(self, params):
        """Update a project"""
        try:
            if self.is_sm:
                project = Project.objects.get(id=params['id'])
            elif self.is_pm:
                project = Project.objects.get(id=params['id'], project_manager=self.user)
            else:
                return {'success': False, 'message': 'You do not have permission to update this project.'}
        except Project.DoesNotExist:
            return {'success': False, 'message': 'Project not found.'}
        
        changes = {}
        if params.get('status'):
            # Projects don't have status, but we can update other fields
            pass
        if params.get('title'):
            changes['title'] = project.title
            project.title = params['title'][:200]
            project.save()
        
        log_change('PROJECT', project.id, 'UPDATE', self.user, changes)
        
        return {
            'success': True,
            'message': f'Project "{project.title}" updated successfully.',
            'entity_id': project.id
        }
    
    def _update_task(self, params):
        """Update a task"""
        try:
            task = Task.objects.get(id=params['id'])
            # Check permissions
            if not (self.is_sm or self.is_pm or task.owner == self.user or self.user in task.responsible_persons.all()):
                return {'success': False, 'message': 'You do not have permission to update this task.'}
        except Task.DoesNotExist:
            return {'success': False, 'message': 'Task not found.'}
        
        changes = {}
        if params.get('status'):
            changes['status'] = task.status
            task.status = params['status']
        if params.get('priority'):
            changes['priority'] = task.priority
            task.priority = params['priority']
        if params.get('due_date'):
            changes['due_date'] = str(task.due_date) if task.due_date else None
            task.due_date = params['due_date']
        
        task.save()
        log_change('TASK', task.id, 'UPDATE', self.user, changes)
        
        return {
            'success': True,
            'message': f'Task "{task.title}" updated successfully.',
            'entity_id': task.id
        }
    
    def _update_event(self, params):
        """Update an event"""
        try:
            event = Event.objects.get(id=params['id'])
            if not (self.is_sm or self.is_pm or event.created_by == self.user):
                return {'success': False, 'message': 'You do not have permission to update this event.'}
        except Event.DoesNotExist:
            return {'success': False, 'message': 'Event not found.'}
        
        changes = {}
        if params.get('status'):
            changes['status'] = event.status
            event.status = params['status']
        
        event.save()
        log_change('EVENT', event.id, 'UPDATE', self.user, changes)
        
        return {
            'success': True,
            'message': f'Event "{event.title}" updated successfully.',
            'entity_id': event.id
        }
    
    def _update_meeting(self, params):
        """Update a meeting"""
        try:
            meeting = Meeting.objects.get(id=params['id'])
            if not (self.is_sm or self.is_pm or self.user in meeting.participants.all()):
                return {'success': False, 'message': 'You do not have permission to update this meeting.'}
        except Meeting.DoesNotExist:
            return {'success': False, 'message': 'Meeting not found.'}
        
        changes = {}
        if params.get('status'):
            changes['status'] = meeting.status
            meeting.status = params['status']
        
        meeting.save()
        
        return {
            'success': True,
            'message': f'Meeting "{meeting.title}" updated successfully.',
            'entity_id': meeting.id
        }
    
    def _delete_entity(self, params):
        """Delete an entity"""
        entity_type = params.get('entity_type')
        entity_id = params.get('id')
        
        if not entity_id:
            return {'success': False, 'message': f'Please specify which {entity_type} to delete (use ID or title).'}
        
        if entity_type == 'project':
            return self._delete_project(params)
        elif entity_type == 'task':
            return self._delete_task(params)
        elif entity_type == 'event':
            return self._delete_event(params)
        elif entity_type == 'meeting':
            return self._delete_meeting(params)
        
        return {'success': False, 'message': f'Unknown entity type: {entity_type}'}
    
    def _delete_project(self, params):
        """Delete a project"""
        try:
            if self.is_sm:
                project = Project.objects.get(id=params['id'])
            elif self.is_pm:
                project = Project.objects.get(id=params['id'], project_manager=self.user)
            else:
                return {'success': False, 'message': 'You do not have permission to delete projects.'}
        except Project.DoesNotExist:
            return {'success': False, 'message': 'Project not found.'}
        
        title = project.title
        project_id = project.id
        project.delete()
        
        log_change('PROJECT', project_id, 'DELETE', self.user, {'title': title})
        
        return {
            'success': True,
            'message': f'Project "{title}" deleted successfully.'
        }
    
    def _delete_task(self, params):
        """Delete a task"""
        try:
            task = Task.objects.get(id=params['id'])
            if not (self.is_sm or self.is_pm or task.owner == self.user):
                return {'success': False, 'message': 'You do not have permission to delete this task.'}
        except Task.DoesNotExist:
            return {'success': False, 'message': 'Task not found.'}
        
        title = task.title
        task_id = task.id
        task.delete()
        
        log_change('TASK', task_id, 'DELETE', self.user, {'title': title})
        
        return {
            'success': True,
            'message': f'Task "{title}" deleted successfully.'
        }
    
    def _delete_event(self, params):
        """Delete an event"""
        try:
            event = Event.objects.get(id=params['id'])
            if not (self.is_sm or self.is_pm or event.created_by == self.user):
                return {'success': False, 'message': 'You do not have permission to delete this event.'}
        except Event.DoesNotExist:
            return {'success': False, 'message': 'Event not found.'}
        
        title = event.title
        event_id = event.id
        event.delete()
        
        log_change('EVENT', event_id, 'DELETE', self.user, {'title': title})
        
        return {
            'success': True,
            'message': f'Event "{title}" deleted successfully.'
        }
    
    def _delete_meeting(self, params):
        """Delete a meeting"""
        try:
            meeting = Meeting.objects.get(id=params['id'])
            # Check if user is participant or has privileges
            if not (self.is_sm or self.is_pm or self.user in meeting.participants.all()):
                return {'success': False, 'message': 'You do not have permission to delete this meeting.'}
        except Meeting.DoesNotExist:
            return {'success': False, 'message': 'Meeting not found.'}
        
        title = meeting.title
        meeting.delete()
        
        return {
            'success': True,
            'message': f'Meeting "{title}" deleted successfully.'
        }


def process_chat_command(user, user_context, message):
    """Main function to process chat commands"""
    handler = CommandHandler(user, user_context)
    
    # First check if it's a command
    command_params = handler.parse_command(message)
    
    if command_params:
        # Execute command
        result = handler.execute_command(command_params)
        return result
    else:
        # Not a command, return None to use regular response handler
        return None

