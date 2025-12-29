# chatbot/response_handler.py

import re
from django.utils import timezone
from datetime import datetime, timedelta


def get_rule_based_response(user_context, user_message, request_user):
    """
    Rule-based response handler for common queries without AI.
    Returns response string or None if no match found.
    Only returns specific, data-driven answers - no generic responses.
    """
    message_lower = user_message.lower().strip()
    
    # Skip rule-based responses for navigation commands (let command handler process them)
    # Check for navigation patterns more specifically
    nav_patterns = [
        r'\bgo\s+to\b',
        r'\bnavigate\s+to\b',
        r'\btake\s+me\s+to\b',
        r'\bopen\s+(my\s+)?(task|project|event|meeting|dashboard)',
        r'\bshow\s+(my\s+)?(task|project|event|meeting|dashboard)',
        r'\bview\s+(my\s+)?(task|project|event|meeting|dashboard)',
    ]
    for pattern in nav_patterns:
        if re.search(pattern, message_lower):
            return None
    
    # Dashboard/Statistics queries - require explicit dashboard/overview/stats keywords
    dashboard_keywords = ['dashboard', 'overview', 'summary', 'statistics', 'stats']
    if any(word in message_lower for word in dashboard_keywords):
        total_projects = user_context.get('total_projects', 0)
        total_tasks = user_context.get('total_tasks', 0)
        total_events = user_context.get('total_events', 0)
        completed_tasks = user_context.get('completed_tasks', 0)
        pending_tasks = user_context.get('pending_tasks', 0)
        
        response = f"Projects: {total_projects} | Tasks: {total_tasks} ({completed_tasks} completed, {pending_tasks} pending) | Events: {total_events}"
        return response
    
    # Project queries - require explicit project keyword
    if 'project' in message_lower or 'projects' in message_lower:
        projects = user_context.get('projects', [])
        if not projects:
            return None  # Let AI handle "no projects" responses
        
        response = ""
        for i, project in enumerate(projects[:5], 1):
            completed = project.get('completed_tasks', 0)
            total = project.get('total_tasks', 0)
            completion = int((completed / total * 100)) if total > 0 else 0
            response += f"{i}. {project.get('title', 'Untitled')} - {completion}% ({completed}/{total} tasks)\n"
        
        if len(projects) > 5:
            response += f"... {len(projects) - 5} more projects"
        
        return response.strip()
    
    # Count queries - check FIRST before listing (for "how many" questions)
    if 'how many' in message_lower:
        if 'project' in message_lower:
            count = user_context.get('total_projects', 0)
            return f"{count} project{'s' if count != 1 else ''}"
        if 'task' in message_lower or 'todo' in message_lower or 'todos' in message_lower:
            tasks = user_context.get('tasks', [])
            # Filter by date if mentioned
            if 'today' in message_lower:
                today = timezone.now().date()
                filtered_tasks = []
                for t in tasks:
                    if t.get('due_date'):
                        try:
                            due_date = datetime.strptime(t.get('due_date'), '%Y-%m-%d').date()
                            if due_date == today:
                                filtered_tasks.append(t)
                        except:
                            pass
                return f"{len(filtered_tasks)} task{'s' if len(filtered_tasks) != 1 else ''} due today"
            elif 'pending' in message_lower:
                filtered_tasks = [t for t in tasks if t.get('status') in ['PENDING', 'UPCOMING']]
                return f"{len(filtered_tasks)} pending task{'s' if len(filtered_tasks) != 1 else ''}"
            else:
                count = user_context.get('total_tasks', 0)
                return f"{count} task{'s' if count != 1 else ''}"
        if 'event' in message_lower:
            count = user_context.get('total_events', 0)
            return f"{count} event{'s' if count != 1 else ''}"
    
    # Task queries - require explicit task/todo keyword (but not "how many")
    if ('task' in message_lower or 'todo' in message_lower or 'todos' in message_lower) and 'how many' not in message_lower:
        tasks = user_context.get('tasks', [])
        if not tasks:
            return None  # Let AI handle "no tasks" responses
        
        # Filter by date if mentioned
        today = timezone.now().date()
        if 'today' in message_lower:
            filtered_tasks = []
            for t in tasks:
                if t.get('due_date'):
                    try:
                        due_date = datetime.strptime(t.get('due_date'), '%Y-%m-%d').date()
                        if due_date == today:
                            filtered_tasks.append(t)
                    except:
                        pass
            if not filtered_tasks:
                return None
            response = ""
            for i, task in enumerate(filtered_tasks[:5], 1):
                response += f"{i}. {task.get('title', 'Untitled')} - {task.get('status', 'N/A')}"
                if task.get('due_date'):
                    response += f" (Due: {task.get('due_date')})"
                response += "\n"
            return response.strip()
        
        # Filter by status if mentioned
        if 'pending' in message_lower or 'upcoming' in message_lower:
            filtered_tasks = [t for t in tasks if t.get('status') in ['PENDING', 'UPCOMING']]
            if not filtered_tasks:
                return None
            response = ""
            for i, task in enumerate(filtered_tasks[:5], 1):
                response += f"{i}. {task.get('title', 'Untitled')}"
                if task.get('due_date'):
                    response += f" (Due: {task.get('due_date')})"
                response += "\n"
            return response.strip()
        
        elif 'completed' in message_lower or 'done' in message_lower:
            filtered_tasks = [t for t in tasks if t.get('status') == 'COMPLETED']
            if not filtered_tasks:
                return None
            response = ""
            for i, task in enumerate(filtered_tasks[:5], 1):
                response += f"{i}. {task.get('title', 'Untitled')}\n"
            return response.strip()
        
        elif 'overdue' in message_lower:
            filtered_tasks = []
            for t in tasks:
                if t.get('due_date') and t.get('status') != 'COMPLETED':
                    try:
                        due_date = datetime.strptime(t.get('due_date'), '%Y-%m-%d').date()
                        if due_date < today:
                            filtered_tasks.append(t)
                    except:
                        pass
            if not filtered_tasks:
                return None
            response = ""
            for i, task in enumerate(filtered_tasks[:5], 1):
                response += f"{i}. {task.get('title', 'Untitled')} (Due: {task.get('due_date')})\n"
            return response.strip()
        
        else:
            # General task query - show first 5
            response = ""
            for i, task in enumerate(tasks[:5], 1):
                response += f"{i}. {task.get('title', 'Untitled')} - {task.get('status', 'N/A')}"
                if task.get('due_date'):
                    response += f" (Due: {task.get('due_date')})"
                response += "\n"
            return response.strip()
    
    # Event queries - require explicit event/meeting keyword
    if 'event' in message_lower or 'events' in message_lower or 'meeting' in message_lower or 'meetings' in message_lower:
        events = user_context.get('events', [])
        if not events:
            return None  # Let AI handle "no events" responses
        
        # Filter upcoming events
        today = timezone.now()
        upcoming_events = []
        for e in events:
            if e.get('start_datetime'):
                try:
                    dt_str = e.get('start_datetime')
                    if 'T' in dt_str:
                        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                    else:
                        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                    if dt > today:
                        upcoming_events.append(e)
                except:
                    pass
        
        if not upcoming_events:
            return None
        
        response = ""
        for i, event in enumerate(upcoming_events[:5], 1):
            response += f"{i}. {event.get('title', 'Untitled')}"
            if event.get('start_datetime'):
                try:
                    dt_str = event.get('start_datetime')
                    if 'T' in dt_str:
                        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                    else:
                        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                    response += f" - {dt.strftime('%b %d, %Y %I:%M %p')}"
                except:
                    pass
            response += "\n"
        return response.strip()
    
    # No match - return None to use AI
    return None

