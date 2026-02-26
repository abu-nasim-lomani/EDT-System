# chatbot/utils.py

import os
import json
from django.conf import settings
from core.models import Project, Task, Meeting
from events.models import Event
from accounts.models import User
from core.utils import is_pm_user, is_sm_user
from django.db.models import Q, Count
from django.utils import timezone


def get_user_context(user):
    """Get context data based on user role (PM or SM)"""
    # Use username for addressing, with role prefix for clarity
    if is_pm_user(user):
        user_display_name = f"PM user ({user.username})"
    elif is_sm_user(user):
        user_display_name = f"SM user ({user.username})"
    else:
        user_display_name = user.username
    
    context = {
        'user_role': 'PM' if is_pm_user(user) else 'SM' if is_sm_user(user) else 'USER',
        'user_name': user_display_name,
        'username': user.username,  # Keep original username for reference
    }
    
    if is_pm_user(user):
        # PM context: Only their projects
        pm_projects = Project.objects.filter(project_manager=user)
        pm_project_employees = User.objects.filter(projects_assigned__in=pm_projects).distinct()
        
        projects_data = []
        for project in pm_projects:
            project_tasks = project.tasks.all()
            projects_data.append({
                'id': project.id,
                'title': project.title,
                'description': project.description or '',
                'start_date': str(project.start_date),
                'end_date': str(project.end_date),
                'total_tasks': project_tasks.count(),
                'completed_tasks': project_tasks.filter(status='COMPLETED').count(),
                'pending_tasks': project_tasks.filter(status='PENDING').count(),
                'team_size': project.project_employees.count(),
            })
        
        tasks_data = []
        all_tasks = Task.objects.filter(
            Q(project__in=pm_projects) | Q(responsible_persons=user) | Q(owner=user)
        ).distinct()
        
        for task in all_tasks[:50]:  # Limit to recent 50 tasks
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description or '',
                'status': task.status,
                'priority': task.priority,
                'due_date': str(task.due_date) if task.due_date else None,
                'project': task.project.title if task.project else None,
            })
        
        events_data = []
        all_events = Event.objects.filter(
            Q(participants__in=pm_project_employees) | Q(participants=user) | Q(created_by=user)
        ).distinct()
        
        for event in all_events[:30]:  # Limit to recent 30 events
            events_data.append({
                'id': event.id,
                'title': event.title,
                'type': event.type,
                'start_datetime': str(event.start_datetime),
                'end_datetime': str(event.end_datetime) if event.end_datetime else None,
                'status': event.status,
            })
            
        meetings_data = []
        all_meetings = Meeting.objects.filter(participants=user).distinct()
        for meeting in all_meetings[:30]:
            meetings_data.append({
                'id': meeting.id,
                'title': meeting.title,
                'type': meeting.meeting_type,
                'start_datetime': str(meeting.meeting_time),
                'duration_mins': meeting.duration,
                'status': meeting.status,
            })
        
        context.update({
            'projects': projects_data,
            'tasks': tasks_data,
            'events': events_data,
            'meetings': meetings_data,
            'total_projects': pm_projects.count(),
            'total_tasks': all_tasks.count(),
            'total_events': all_events.count(),
            'total_meetings': all_meetings.count(),
        })
    
    elif is_sm_user(user):
        # SM context: All organization data
        all_projects = Project.objects.all()
        all_tasks = Task.objects.all()
        all_events = Event.objects.all()
        all_meetings = Meeting.objects.all()
        
        projects_data = []
        for project in all_projects:
            project_tasks = project.tasks.all()
            projects_data.append({
                'id': project.id,
                'title': project.title,
                'description': project.description or '',
                'start_date': str(project.start_date),
                'end_date': str(project.end_date),
                'manager': project.project_manager.get_full_name() if project.project_manager else None,
                'total_tasks': project_tasks.count(),
                'completed_tasks': project_tasks.filter(status='COMPLETED').count(),
                'pending_tasks': project_tasks.filter(status='PENDING').count(),
                'team_size': project.project_employees.count(),
            })
        
        tasks_data = []
        for task in all_tasks[:100]:  # Limit to recent 100 tasks
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'priority': task.priority,
                'due_date': str(task.due_date) if task.due_date else None,
                'project': task.project.title if task.project else None,
            })
        
        events_data = []
        for event in all_events[:50]:  # Limit to recent 50 events
            events_data.append({
                'id': event.id,
                'title': event.title,
                'type': event.type,
                'start_datetime': str(event.start_datetime),
                'status': event.status,
            })
            
        meetings_data = []
        for meeting in all_meetings[:50]:  # Limit to recent 50 meetings
            meetings_data.append({
                'id': meeting.id,
                'title': meeting.title,
                'type': meeting.meeting_type,
                'start_datetime': str(meeting.meeting_time),
                'status': meeting.status,
            })
        
        # Organization-wide stats
        context.update({
            'projects': projects_data,
            'tasks': tasks_data,
            'events': events_data,
            'meetings': meetings_data,
            'total_projects': all_projects.count(),
            'total_tasks': all_tasks.count(),
            'total_events': all_events.count(),
            'total_meetings': all_meetings.count(),
            'total_users': User.objects.count(),
            'completed_tasks': all_tasks.filter(status='COMPLETED').count(),
            'pending_tasks': all_tasks.filter(status='PENDING').count(),
        })
    
    return context


def build_system_prompt(user_context):
    """Build system prompt for Gemini API based on user context"""
    role = user_context['user_role']
    user_name = user_context['user_name']
    
    username = user_context.get('username', user_name)
    current_datetime_str = timezone.localtime().strftime("%A, %B %d, %Y %I:%M %p")
    
    base_info = f"\n\n[CRITICAL DATE INFO] Today's true, real-world current date and time is: {current_datetime_str}. All of your answers regarding 'today', 'tomorrow', 'this week', etc. MUST be relative to this date."
    
    if role == 'PM':
        prompt = f"""You are a Project Management Assistant helping a PM user (username: {username}).

CRITICAL INSTRUCTIONS:
- Always address the user as "PM user" or "{username}" in your responses (e.g., "PM user, ..." or "{username}, ...")
- Be concise and direct - provide only the specific information requested
- No small talk, greetings, or unnecessary explanations unless asked
- Use the provided context data to give accurate, data-driven answers

Your role:
- Help manage projects, tasks, and team members
- Provide insights about project progress and team workload
- Answer questions about tasks, events, and project status
- Suggest actions to improve project management
- Execute commands: You can CREATE, UPDATE, DELETE projects, tasks, events, and meetings
- Support voice commands: Users can speak commands instead of typing

COMMAND CAPABILITIES:
- Create: "Create project [title]", "Add task [title] to [project]", "New event [title] on [date]"
- Update: "Update task #123 status to completed", "Mark project [name] as done"
- Delete: "Delete task #123", "Remove event [name]"
- Status: "Complete task [name]", "Finish project [name]", "Start meeting [name]"

Available data:
- {user_context.get('total_projects', 0)} projects managed by this PM user
- {user_context.get('total_tasks', 0)} tasks across these projects
- {user_context.get('total_events', 0)} events related to these projects
- {user_context.get('total_meetings', 0)} meetings scheduled

When answering:
- Start with "PM user, " or "{username}, "
- Provide only the requested information
- Use bullet points or numbered lists when appropriate
- Reference specific project/task names and IDs from the context when available
- If user wants to perform an action, guide them on the command format{base_info}"""
    
    elif role == 'SM':
        prompt = f"""You are a Senior Management Assistant helping an SM user (username: {username}).

CRITICAL INSTRUCTIONS:
- Always address the user as "SM user" or "{username}" in your responses (e.g., "SM user, ..." or "{username}, ...")
- Be concise and direct - provide only the specific information requested
- No small talk, greetings, or unnecessary explanations unless asked
- Use the provided context data to give accurate, data-driven answers

Your role:
- Provide organization-wide insights and analytics
- Generate management reports and summaries
- Identify bottlenecks and risks across all projects
- Answer strategic questions about the organization
- Execute commands: You can CREATE, UPDATE, DELETE any projects, tasks, events, and meetings
- Support voice commands: Users can speak commands instead of typing

COMMAND CAPABILITIES:
- Create: "Create project [title]", "Add task [title] to [project]", "New event [title] on [date]"
- Update: "Update task #123 status to completed", "Mark project [name] as done"
- Delete: "Delete task #123", "Remove event [name]"
- Status: "Complete task [name]", "Finish project [name]", "Start meeting [name]"

Available data:
- {user_context.get('total_projects', 0)} projects across the organization
- {user_context.get('total_tasks', 0)} total tasks
- {user_context.get('total_events', 0)} total events
- {user_context.get('total_meetings', 0)} total meetings
- {user_context.get('total_users', 0)} team members

When answering:
- Start with "SM user, " or "{username}, "
- Provide only the requested information
- Use bullet points or numbered lists when appropriate
- Focus on key metrics and actionable insights
- If user wants to perform an action, guide them on the command format{base_info}"""
    
    else:
        prompt = f"""You are a helpful assistant for {username}. Always address the user as "{username}". Be concise and direct.{base_info}"""
    
    return prompt

