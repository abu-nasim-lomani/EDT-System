# Quick Start: Deploy to PythonAnywhere

This guide will help you deploy your Django EDT application to PythonAnywhere quickly.

## Prerequisites

1. PythonAnywhere account (free or paid)
2. Gemini API key (for chatbot functionality)
3. Your code ready in a Git repository (recommended)

## Fast Track Deployment

### 1. Upload Your Code

**Option A: Using Git (Recommended)**
```bash
cd ~
git clone <your-repo-url> edt
cd edt
```

**Option B: Manual Upload**
- Use PythonAnywhere's Files tab to upload your project

### 2. Run Setup Script

```bash
cd ~/edt
chmod +x setup_pythonanywhere.sh
bash setup_pythonanywhere.sh
```

This script will:
- Create virtual environment
- Install dependencies
- Build Tailwind CSS (if Node.js available)
- Collect static files
- Run migrations

### 3. Configure Environment Variables

Go to **Web** tab → **Web app** → **Environment variables** and add:

```
SECRET_KEY=<generate-a-new-secret-key>
DEBUG=False
GEMINI_API_KEY=<your-gemini-api-key>
PYTHONANYWHERE_HOSTNAME=yourusername.pythonanywhere.com
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Configure WSGI

1. Go to **Web** tab → **WSGI configuration file**
2. Copy contents from `pythonanywhere_wsgi.py`
3. Update the path: `/home/yourusername/edt`
4. Save

### 5. Configure Static Files

In **Web** tab → **Static files**:
- **URL:** `/static/`
- **Directory:** `/home/yourusername/edt/staticfiles/`

### 6. Create Superuser

```bash
cd ~/edt
source venv/bin/activate
python manage.py createsuperuser
```

### 7. Reload Web App

Click the green **Reload** button in the Web tab.

### 8. Test Your Site

Visit: `https://yourusername.pythonanywhere.com`

## Detailed Documentation

For comprehensive deployment instructions, troubleshooting, and maintenance:

- **Full Guide:** `PYTHONANYWHERE_DEPLOYMENT.md`
- **Checklist:** `DEPLOYMENT_CHECKLIST.md`
- **Pre-deployment Script:** `build_for_deployment.py`

## Common Issues

### Static Files Not Loading
- Ensure `collectstatic` was run
- Check static files mapping in Web tab
- Verify file permissions: `chmod -R 755 staticfiles/`

### 500 Internal Server Error
- Check Error log in Web tab
- Verify all environment variables are set
- Ensure `ALLOWED_HOSTS` includes your domain

### Tailwind CSS Not Working
- Build Tailwind CSS: `cd theme/static_src && npm run build`
- Or upload pre-compiled CSS from local build

## Need Help?

- Check `PYTHONANYWHERE_DEPLOYMENT.md` for detailed troubleshooting
- PythonAnywhere Help: https://help.pythonanywhere.com/
- Django Docs: https://docs.djangoproject.com/


