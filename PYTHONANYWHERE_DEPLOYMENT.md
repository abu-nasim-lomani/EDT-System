# PythonAnywhere Deployment Guide

Complete guide to deploy your Django EDT (Event and Decision Tracker) application on PythonAnywhere.

## Prerequisites

1. **PythonAnywhere Account**
   - Free account: Limited features, SQLite database
   - Paid account ($5/month): MySQL database, Node.js support, better performance

2. **Required Information**
   - Gemini API Key (from Google AI Studio)
   - PythonAnywhere username
   - Domain name (e.g., `yourusername.pythonanywhere.com`)

## Pre-Deployment Steps (Local)

### 1. Build Tailwind CSS

Before deploying, compile your Tailwind CSS:

```bash
cd theme/static_src
npm install
npm run build
cd ../..
```

This creates the compiled CSS file at `theme/static/css/dist/styles.css`.

**Note:** If you have a paid PythonAnywhere account with Node.js, you can skip this and build on the server.

### 2. Collect Static Files Locally (Optional)

```bash
python manage.py collectstatic --noinput
```

### 3. Prepare Environment Variables

Create a `.env` file template (don't commit actual keys):

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-pro
PYTHONANYWHERE_HOSTNAME=yourusername.pythonanywhere.com
```

## Deployment Steps on PythonAnywhere

### Step 1: Upload Your Code

**Option A: Using Git (Recommended)**
```bash
# In PythonAnywhere Bash console
cd ~
git clone https://github.com/yourusername/your-repo.git edt
cd edt
```

**Option B: Manual Upload**
- Use PythonAnywhere's Files tab
- Upload your project files (excluding `venv/`, `__pycache__/`, `.env`)

### Step 2: Set Up Virtual Environment

```bash
cd ~/edt
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** PythonAnywhere uses Python 3.10 by default. Adjust version if needed.

### Step 3: Configure Environment Variables

1. Go to **Web** tab → **Web app** → **Environment variables**
2. Add these variables:

```
SECRET_KEY=your-actual-secret-key
DEBUG=False
GEMINI_API_KEY=your-actual-gemini-api-key
GEMINI_MODEL=gemini-2.5-pro
PYTHONANYWHERE_HOSTNAME=yourusername.pythonanywhere.com
```

**Important:** Generate a new SECRET_KEY for production:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 4: Build Tailwind CSS (If Paid Account)

If you have Node.js support:

```bash
cd ~/edt/theme/static_src
npm install
npm run build
cd ~/edt
```

Otherwise, ensure you've built it locally and uploaded the compiled CSS.

### Step 5: Set Up Database

**For Free Accounts (SQLite):**
```bash
cd ~/edt
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

**For Paid Accounts (MySQL):**
1. Go to **Databases** tab → Create MySQL database
2. Update environment variables:
   ```
   DATABASE_URL=mysql://username:password@hostname/database_name
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

### Step 6: Collect Static Files

```bash
cd ~/edt
source venv/bin/activate
python manage.py collectstatic --noinput
```

### Step 7: Configure WSGI File

1. Go to **Web** tab → **Web app**
2. Click on **WSGI configuration file** link
3. Replace the content with the provided `pythonanywhere_wsgi.py` template
4. Update the path to your project if different

### Step 8: Configure Static Files Mapping

In **Web** tab → **Static files**:

- **URL:** `/static/`
- **Directory:** `/home/yourusername/edt/staticfiles/`

### Step 9: Reload Web App

Click the green **Reload** button in the Web tab.

## Post-Deployment

### Verify Deployment

1. Visit `https://yourusername.pythonanywhere.com`
2. Test login functionality
3. Test chatbot (requires Gemini API key)
4. Check static files are loading (CSS, JS)

### Common Issues & Solutions

#### Issue: Static files not loading
- **Solution:** Check Static files mapping in Web tab
- Verify `collectstatic` was run
- Check file permissions: `chmod -R 755 staticfiles/`

#### Issue: Database errors
- **Solution:** Ensure migrations ran successfully
- Check database permissions
- Verify `DATABASE_URL` environment variable (for MySQL)

#### Issue: Tailwind CSS not working
- **Solution:** Ensure `theme/static/css/dist/styles.css` exists
- Rebuild Tailwind CSS if needed
- Check static files mapping

#### Issue: Gemini API errors
- **Solution:** Verify `GEMINI_API_KEY` is set correctly
- Check API key has quota remaining
- Review error logs in Web tab → **Error log**

#### Issue: 500 Internal Server Error
- **Solution:** Check **Error log** in Web tab
- Verify all environment variables are set
- Check `ALLOWED_HOSTS` includes your domain

### Monitoring

- **Error Logs:** Web tab → **Error log**
- **Server Logs:** Web tab → **Server log**
- **Task Logs:** Tasks tab (for scheduled tasks)

## Scheduled Tasks (Optional)

If you need cron jobs, use PythonAnywhere's **Tasks** tab:

```bash
# Example: Daily database backup
0 2 * * * cd ~/edt && source venv/bin/activate && python manage.py dumpdata > backup.json
```

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] `.env` file not committed to Git
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] CSRF protection enabled (default in Django)
- [ ] HTTPS enabled (automatic on PythonAnywhere)
- [ ] API keys stored in environment variables only

## Backup Strategy

1. **Database Backup:**
   ```bash
   python manage.py dumpdata > backup_$(date +%Y%m%d).json
   ```

2. **Code Backup:**
   - Use Git for version control
   - Regular commits to repository

## Updating Your Application

1. Pull latest changes (if using Git):
   ```bash
   cd ~/edt
   git pull
   ```

2. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Update dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Rebuild Tailwind (if CSS changed):
   ```bash
   cd theme/static_src && npm run build && cd ../..
   ```

6. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

7. Reload web app in Web tab

## Support

- PythonAnywhere Docs: https://help.pythonanywhere.com/
- Django Deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
- Project Issues: Check your repository's issue tracker


