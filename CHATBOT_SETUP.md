# Chatbot Setup Guide

## Overview
The chatbot feature provides an AI-powered assistant for PM (Project Manager) and SM (Senior Management) users. It uses Google's Gemini API to provide intelligent responses about projects, tasks, events, and generate reports.

## Prerequisites
- Python 3.8+
- Django 5.2+
- Google Gemini API Key

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install `google-generativeai` package along with other dependencies.

### 2. Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 3. Configure Environment Variables
Create or update your `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Select Gemini model (defaults to gemini-2.5-pro)
# Options: gemini-2.5-pro (best quality) or gemini-2.5-flash (faster)
GEMINI_MODEL=gemini-2.5-pro
```

**Important:** Never commit your API key to version control. The `.env` file should be in `.gitignore`.

**Model Selection:**
- `gemini-2.5-pro`: Best for complex tasks, longer context, higher quality responses (default)
- `gemini-2.5-flash`: Faster responses, good for most standard tasks, more cost-effective

### 4. Run Migrations
```bash
python manage.py migrate chatbot
```

This will create the necessary database tables for storing conversations and messages.

### 5. Access the Chatbot
- The chatbot widget appears as a floating button in the bottom-right corner
- Only visible to PM and SM users
- Click the button to open the chat interface

## Features

### For PM Users:
- View project status and progress
- Check task assignments and deadlines
- Get team workload insights
- Generate project reports
- Ask questions about their managed projects

### For SM Users:
- Organization-wide analytics
- Cross-project insights
- Management reports
- Strategic recommendations
- View all projects, tasks, and events

## Usage Examples

### PM User Queries:
- "What's the status of my projects?"
- "Show me overdue tasks"
- "Which team members are overloaded?"
- "Generate a project status report"

### SM User Queries:
- "Show me all projects across the organization"
- "Which projects are behind schedule?"
- "Generate a management report"
- "What are the bottlenecks in our projects?"

## API Endpoints

- `GET /api/chatbot/message/` - Get conversation history
- `POST /api/chatbot/message/` - Send a message and get AI response
- `POST /api/chatbot/new/` - Create a new conversation
- `GET /api/chatbot/conversations/` - List all conversations

## Troubleshooting

### Chatbot not appearing?
- Ensure you're logged in as a PM or SM user
- Check browser console for JavaScript errors
- Verify Alpine.js is loaded

### API errors?
- Check that `GEMINI_API_KEY` is set in your `.env` file
- Verify the API key is valid and has quota remaining
- Check Django logs for detailed error messages

### Messages not saving?
- Ensure migrations have been run
- Check database permissions
- Verify chatbot app is in `INSTALLED_APPS`

## Security Notes

- All API endpoints require authentication (`@login_required`)
- Only PM and SM users can access the chatbot
- CSRF protection is enabled for all POST requests
- API keys should never be exposed in client-side code

## Customization

### Modify System Prompts
Edit `chatbot/utils.py` → `build_system_prompt()` function to customize AI behavior.

### Change Widget Appearance
Edit `chatbot/templates/chatbot/chat_widget.html` to modify the UI.

### Adjust Context Data
Edit `chatbot/utils.py` → `get_user_context()` function to change what data is sent to the AI.

## Support

For issues or questions, check:
1. Django logs: `python manage.py runserver` output
2. Browser console: F12 → Console tab
3. Database: Check `chatbot_chatconversation` and `chatbot_chatmessage` tables

