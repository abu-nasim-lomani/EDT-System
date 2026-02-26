# chatbot/views.py

import json
import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import ChatConversation, ChatMessage
from .utils import get_user_context, build_system_prompt
from core.utils import is_pm_user, is_sm_user
from django.core.exceptions import PermissionDenied

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def get_openai_client():
    """
    Initialize and return OpenAI client.

    Available models:
    - 'gpt-4o'       : Best quality, latest flagship
    - 'gpt-4o-mini'  : Faster & cheaper, great for most tasks
    - 'gpt-3.5-turbo': Budget option
    """
    if not OPENAI_AVAILABLE:
        return None

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return None

    return OpenAI(api_key=api_key)


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
        # Don't auto-create conversations. Just get the most recent one.
        conversation_id = request.GET.get('conversation_id')
        
        if conversation_id:
            try:
                conversation = ChatConversation.objects.get(id=conversation_id, user=request.user)
            except ChatConversation.DoesNotExist:
                conversation = ChatConversation.objects.filter(user=request.user).order_by('-updated_at').first()
        else:
            conversation = ChatConversation.objects.filter(user=request.user).order_by('-updated_at').first()

        
        if not conversation:
            return JsonResponse({
                'conversation_id': None,
                'messages': []
            })

        # Get recent messages
        messages = conversation.messages.all()[:50]  # Last 50 messages
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
            voice_mode = data.get('voice_mode', False)  # True when user spoke via mic

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

            # Voice mode: make the AI sound like a real human speaking
            if voice_mode:
                system_prompt += (
                    "\n\n[VOICE MODE ACTIVE] You are speaking aloud to the user. "
                    "Respond in a warm, natural, conversational tone — like a knowledgeable colleague speaking. "
                    "Keep replies to 1-3 short, clear sentences. "
                    "Never use markdown formatting (no bullet points, asterisks, dashes, or headers). "
                    "Do not say things like 'As an AI' or 'Certainly!'. "
                    "Speak directly and naturally, as if in a real conversation."
                )

            # Prepare context text
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

Scheduled Meetings:
{json.dumps(user_context.get('meetings', [])[:10], indent=2)}
"""

            # Get conversation history for OpenAI messages list
            recent_messages = conversation.messages.all()[:10]
            conversation_history = []
            for msg in recent_messages:
                role = msg.role if msg.role in ('user', 'assistant') else 'user'
                conversation_history.append({
                    'role': role,
                    'content': msg.content
                })

            # Try command handler first (for CRUD operations and navigation)
            from .command_handler import process_chat_command
            command_result = process_chat_command(request.user, user_context, message_content)

            if command_result:
                if command_result.get('success'):
                    assistant_response = command_result.get('message', 'Command executed successfully.')
                    metadata = {
                        'command_executed': True,
                        'entity_type': command_result.get('entity_type'),
                        'entity_id': command_result.get('entity_id')
                    }
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
                if command_result.get('navigate'):
                    response_data['navigate'] = True
                    response_data['url'] = command_result.get('url')

                return JsonResponse(response_data)

            # Try rule-based response (works without AI)
            from .response_handler import get_rule_based_response
            rule_based_response = get_rule_based_response(user_context, message_content, request.user)

            if rule_based_response:
                assistant_response = rule_based_response
            else:
                # Use OpenAI API
                preferred_model = data.get('model', os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'))
                client = get_openai_client()

                if client:
                    username = user_context.get('username', user_context['user_name'])
                    user_role_display = 'SM user' if is_sm_user(request.user) else 'PM user' if is_pm_user(request.user) else 'user'

                    # Build OpenAI messages array
                    openai_messages = [
                        {
                            'role': 'system',
                            'content': f"{system_prompt}\n\n{context_text}"
                        }
                    ]
                    # Add conversation history
                    openai_messages.extend(conversation_history)
                    # Add current user message
                    openai_messages.append({
                        'role': 'user',
                        'content': f"User Question: {message_content}\n\nProvide a direct, concise answer addressing the {user_role_display} ({username}). Use only the context data provided above."
                    })

                    try:
                        response = client.chat.completions.create(
                            model=preferred_model,
                            messages=openai_messages,
                            max_tokens=1000,
                            temperature=0.7,
                        )
                        assistant_response = response.choices[0].message.content
                    except Exception as e:
                        assistant_response = f"Error: {str(e)}"
                else:
                    return JsonResponse({
                        'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY in .env file.',
                        'conversation_id': conversation.id,
                        'messages': []
                    }, status=400, content_type='application/json')

            # Save assistant message
            assistant_message = ChatMessage.objects.create(
                conversation=conversation,
                role=ChatMessage.MessageRole.ASSISTANT,
                content=assistant_response
            )

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
@require_http_methods(["POST"])
def stt_view(request):
    """
    Speech-to-Text using OpenAI Whisper.
    Accepts a multipart audio file, returns {"transcript": "..."}.
    Whisper auto-detects language — supports Bengali + English.
    """
    if not (is_pm_user(request.user) or is_sm_user(request.user)):
        return JsonResponse({'error': 'Access denied'}, status=403)

    audio_file = request.FILES.get('audio')
    if not audio_file:
        return JsonResponse({'error': 'No audio file provided'}, status=400)

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key or not OPENAI_AVAILABLE:
        return JsonResponse({'error': 'OpenAI API not configured'}, status=400)

    try:
        client = OpenAI(api_key=api_key)
        # Give file a name hint so Whisper knows it's an audio file
        audio_file.name = audio_file.name or 'audio.webm'
        transcript = client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            # language=None → auto-detect (Bengali, English, etc.)
        )
        return JsonResponse({'transcript': transcript.text})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def tts_view(request):
    """
    Text-to-Speech using OpenAI TTS-HD.
    Accepts JSON {"text": "...", "voice": "shimmer"} and streams back MP3 audio.
    HD voices (most natural): shimmer (warm female), nova (energetic), alloy (neutral male)
    """
    if not (is_pm_user(request.user) or is_sm_user(request.user)):
        return HttpResponse('Access denied', status=403)

    try:
        data = json.loads(request.body)
        raw_text = data.get('text', '').strip()
        voice = data.get('voice', 'shimmer')  # shimmer = warmest, most human-sounding
        if not raw_text:
            return HttpResponse('No text provided', status=400)

        # Clean markdown/symbols so TTS sounds natural
        import re
        clean = re.sub(r'[*_`#>~|]', '', raw_text)          # remove markdown chars
        clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)  # [text](url) → text
        clean = re.sub(r'\n{2,}', '. ', clean)               # double newlines → pause
        clean = re.sub(r'\n', ' ', clean)                    # single newline → space
        clean = re.sub(r' {2,}', ' ', clean).strip()         # collapse spaces
        clean = clean[:2000]  # keep under limit

        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key or not OPENAI_AVAILABLE:
            return HttpResponse('OpenAI API not configured', status=400)

        client = OpenAI(api_key=api_key)
        response = client.audio.speech.create(
            model='tts-1-hd',   # HD = much more natural and human-like
            voice=voice,
            input=clean,
            response_format='mp3',
            speed=0.95,         # slightly slower = more natural speech cadence
        )
        audio_bytes = response.read()
        return HttpResponse(audio_bytes, content_type='audio/mpeg')
    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON', status=400)
    except Exception as e:
        return HttpResponse(str(e), status=500)


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
def chat_page(request):
    """Render the full-page chat UI"""
    from django.shortcuts import render, redirect
    if not (is_pm_user(request.user) or is_sm_user(request.user)):
        from django.contrib import messages
        messages.warning(request, 'The AI Assistant is only available for PM and SM users.')
        return redirect('meeting_list')
    return render(request, 'chatbot/chat.html')


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
