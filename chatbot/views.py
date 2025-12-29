# chatbot/views.py

import json
import os
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import ChatConversation, ChatMessage
from .utils import get_user_context, build_system_prompt
from core.utils import is_pm_user, is_sm_user
from django.core.exceptions import PermissionDenied

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def get_gemini_client(model_name='gemini-2.5-pro'):
    """
    Initialize and return Gemini client
    
    Available models:
    - 'gemini-2.5-pro': Best for complex tasks, longer context
    - 'gemini-2.5-flash': Faster responses, good for most tasks
    """
    if not GEMINI_AVAILABLE:
        return None
    
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return None
    
    genai.configure(api_key=api_key)
    
    # Use Gemini 2.5 models
    valid_models = ['gemini-2.5-pro', 'gemini-2.5-flash']
    if model_name not in valid_models:
        model_name = 'gemini-2.5-pro'  # Default to pro
    
    try:
        return genai.GenerativeModel(model_name)
    except Exception:
        # Fallback to gemini-2.5-flash if pro is not available
        try:
            return genai.GenerativeModel('gemini-2.5-flash')
        except Exception:
            # Last fallback to older model
            return genai.GenerativeModel('gemini-pro')


@login_required
@require_http_methods(["GET", "POST"])
def chat_message(request):
    """Handle chat messages and return AI responses"""
    # Check if user is PM or SM
    if not (is_pm_user(request.user) or is_sm_user(request.user)):
        return JsonResponse({
            'error': 'Access denied. Only PM and SM users can use the chatbot.',
            'conversation_id': None,
            'messages': []
        }, status=403, content_type='application/json')
    
    if request.method == 'GET':
        # Get or create conversation
        conversation, created = ChatConversation.objects.get_or_create(
            user=request.user,
            defaults={'title': f'Chat {timezone.now().strftime("%Y-%m-%d %H:%M")}'}
        )
        
        # Get recent messages
        messages = conversation.messages.all()[:20]  # Last 20 messages
        messages_data = [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]
        
        return JsonResponse({
            'conversation_id': conversation.id,
            'messages': messages_data
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            message_content = data.get('message', '').strip()
            conversation_id = data.get('conversation_id')
            
            if not message_content:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
            # Get or create conversation
            if conversation_id:
                try:
                    conversation = ChatConversation.objects.get(id=conversation_id, user=request.user)
                except ChatConversation.DoesNotExist:
                    conversation = ChatConversation.objects.create(user=request.user)
            else:
                conversation = ChatConversation.objects.create(user=request.user)
            
            # Save user message
            user_message = ChatMessage.objects.create(
                conversation=conversation,
                role=ChatMessage.MessageRole.USER,
                content=message_content
            )
            
            # Get user context
            user_context = get_user_context(request.user)
            system_prompt = build_system_prompt(user_context)
            
            # Prepare context for Gemini
            context_text = f"""
User Context:
- Role: {user_context['user_role']}
- Name: {user_context['user_name']}
- Total Projects: {user_context.get('total_projects', 0)}
- Total Tasks: {user_context.get('total_tasks', 0)}
- Total Events: {user_context.get('total_events', 0)}

Recent Projects:
{json.dumps(user_context.get('projects', [])[:10], indent=2)}

Recent Tasks:
{json.dumps(user_context.get('tasks', [])[:20], indent=2)}

Recent Events:
{json.dumps(user_context.get('events', [])[:10], indent=2)}
"""
            
            # Get conversation history
            recent_messages = conversation.messages.all()[:10]
            conversation_history = []
            for msg in recent_messages:
                conversation_history.append({
                    'role': msg.role,
                    'parts': [msg.content]
                })
            
            # Try command handler first (for CRUD operations and navigation)
            from .command_handler import process_chat_command
            command_result = process_chat_command(request.user, user_context, message_content)
            
            if command_result:
                # Command was executed
                if command_result.get('success'):
                    assistant_response = command_result.get('message', 'Command executed successfully.')
                    # Store command metadata
                    metadata = {
                        'command_executed': True,
                        'entity_type': command_result.get('entity_type'),
                        'entity_id': command_result.get('entity_id')
                    }
                    
                    # Add navigation URL if it's a navigation command
                    if command_result.get('navigate'):
                        metadata['navigate'] = True
                        metadata['url'] = command_result.get('url')
                    
                    assistant_message = ChatMessage.objects.create(
                        conversation=conversation,
                        role=ChatMessage.MessageRole.ASSISTANT,
                        content=assistant_response,
                        metadata=metadata
                    )
                else:
                    assistant_response = command_result.get('message', 'Command failed.')
                    assistant_message = ChatMessage.objects.create(
                        conversation=conversation,
                        role=ChatMessage.MessageRole.ASSISTANT,
                        content=assistant_response
                    )
                
                conversation.save()
                response_data = {
                    'conversation_id': conversation.id,
                    'response': assistant_response,
                    'timestamp': assistant_message.timestamp.isoformat(),
                    'command_executed': True
                }
                
                # Add navigation URL if it's a navigation command
                if command_result.get('navigate'):
                    response_data['navigate'] = True
                    response_data['url'] = command_result.get('url')
                
                return JsonResponse(response_data)
            
            # Try rule-based response (works without AI) - only if not a navigation command
            from .response_handler import get_rule_based_response
            rule_based_response = get_rule_based_response(user_context, message_content, request.user)
            
            if rule_based_response:
                # Use rule-based response (no AI needed)
                assistant_response = rule_based_response
            else:
                # Try AI if available
                preferred_model = data.get('model', os.environ.get('GEMINI_MODEL', 'gemini-2.5-pro'))
                client = get_gemini_client(model_name=preferred_model)
                
                if client:
                    # Build prompt with system instructions
                    username = user_context.get('username', user_context['user_name'])
                    user_role_display = 'SM user' if is_sm_user(request.user) else 'PM user' if is_pm_user(request.user) else 'user'
                    full_prompt = f"{system_prompt}\n\n{context_text}\n\nUser Question: {message_content}\n\nProvide a direct, concise answer addressing the {user_role_display} ({username}) by saying '{user_role_display}' or '{username}'. Use only the context data provided above."
                    
                    try:
                        response = client.generate_content(full_prompt)
                        assistant_response = response.text
                    except Exception as e:
                        assistant_response = f"Error: {str(e)}"
                else:
                    # No AI available and no rule-based match - return None to indicate no response
                    return JsonResponse({
                        'error': 'Unable to process this query. Please ask about projects, tasks, events, or dashboard statistics.',
                        'conversation_id': conversation.id,
                        'messages': []
                    }, status=400, content_type='application/json')
            
            # Save assistant message
            assistant_message = ChatMessage.objects.create(
                conversation=conversation,
                role=ChatMessage.MessageRole.ASSISTANT,
                content=assistant_response
            )
            
            # Update conversation timestamp
            conversation.save()
            
            return JsonResponse({
                'conversation_id': conversation.id,
                'response': assistant_response,
                'timestamp': assistant_message.timestamp.isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def chat_conversations(request):
    """Get list of user's conversations"""
    if not (is_pm_user(request.user) or is_sm_user(request.user)):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    conversations = ChatConversation.objects.filter(user=request.user).order_by('-updated_at')[:10]
    conversations_data = [
        {
            'id': conv.id,
            'title': conv.title or f'Chat {conv.id}',
            'created_at': conv.created_at.isoformat(),
            'updated_at': conv.updated_at.isoformat(),
            'message_count': conv.messages.count()
        }
        for conv in conversations
    ]
    
    return JsonResponse({'conversations': conversations_data})


@login_required
@require_http_methods(["POST"])
def new_conversation(request):
    """Create a new conversation"""
    if not (is_pm_user(request.user) or is_sm_user(request.user)):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    conversation = ChatConversation.objects.create(
        user=request.user,
        title=f'Chat {timezone.now().strftime("%Y-%m-%d %H:%M")}'
    )
    
    return JsonResponse({
        'conversation_id': conversation.id,
        'title': conversation.title
    })
