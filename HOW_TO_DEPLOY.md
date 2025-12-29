# Step-by-Step Deployment Guide to PythonAnywhere

Follow these steps to deploy your Django EDT application to PythonAnywhere.

## 📋 Prerequisites

- PythonAnywhere account (sign up at https://www.pythonanywhere.com)
- Gemini API key (for chatbot functionality)
- Your code in a Git repository (recommended) or ready to upload

---

## 🏠 STEP 1: Prepare Your Code Locally

### 1.1 Build Tailwind CSS

Open PowerShell/Terminal in your project directory and run:

```bash
cd theme/static_src
npm install
npm run build
cd ../..
```

This creates `theme/static/css/dist/styles.css` - **required for styling to work!**

### 1.2 (Optional) Run Pre-Deployment Check

```bash
python build_for_deployment.py
```

This will verify everything is ready.

### 1.3 Commit Your Code

```bash
git add .
git commit -m "Ready for PythonAnywhere deployment"
git push
```

---

## ☁️ STEP 2: Upload Code to PythonAnywhere

### Option A: Using Git (Recommended)

1. Log into PythonAnywhere
2. Open the **Bash** console
3. Run:

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git edt
cd edt
```

Replace `YOUR_USERNAME/YOUR_REPO` with your actual GitHub repository URL.

### Option B: Manual Upload

1. Go to **Files** tab in PythonAnywhere
2. Navigate to `/home/yourusername/`
3. Upload your project files (zip and extract, or upload folder by folder)
4. Make sure you're in `/home/yourusername/edt/` directory

---

## ⚙️ STEP 3: Set Up Virtual Environment

In PythonAnywhere **Bash** console:

```bash
cd ~/edt
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** This may take a few minutes. PythonAnywhere uses Python 3.10 by default.

---

## 🔑 STEP 4: Configure Environment Variables

1. Go to **Web** tab in PythonAnywhere dashboard
2. Click on your web app (or create a new one)
3. Scroll down to **Environment variables**
4. Add these variables:

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
GEMINI_API_KEY=your-gemini-api-key-here
PYTHONANYWHERE_HOSTNAME=yourusername.pythonanywhere.com
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the generated key and paste it as the `SECRET_KEY` value.

**Important:** Replace `yourusername` with your actual PythonAnywhere username!

---

## 🗄️ STEP 5: Set Up Database

### For Free Accounts (SQLite):

```bash
cd ~/edt
source venv/bin/activate
python manage.py migrate
```

### For Paid Accounts (MySQL):

1. Go to **Databases** tab
2. Create a MySQL database
3. Note the database credentials
4. Add to environment variables:
   ```
   DATABASE_URL=mysql://username:password@hostname/database_name
   ```
5. Run migrations:
   ```bash
   cd ~/edt
   source venv/bin/activate
   python manage.py migrate
   ```

---

## 📁 STEP 6: Collect Static Files

```bash
cd ~/edt
source venv/bin/activate
python manage.py collectstatic --noinput
```

This creates the `staticfiles/` directory with all CSS, JS, and images.

---

## 🔧 STEP 7: Configure WSGI File

1. Go to **Web** tab
2. Click on **WSGI configuration file** link
3. **Delete all existing content**
4. Copy and paste this (replace `yourusername` with your actual username):

```python
import os
import sys

path = '/home/yourusername/edt'  # CHANGE yourusername to your actual username
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. Click **Save**

---

## 📂 STEP 8: Configure Static Files Mapping

1. Still in **Web** tab
2. Scroll to **Static files** section
3. Add a new mapping:
   - **URL:** `/static/`
   - **Directory:** `/home/yourusername/edt/staticfiles/`
4. Click **Save**

---

## 👤 STEP 9: Create Superuser

```bash
cd ~/edt
source venv/bin/activate
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

---

## 🚀 STEP 10: Reload Web App

1. Go back to **Web** tab
2. Click the big green **Reload** button
3. Wait for it to reload (may take 10-30 seconds)

---

## ✅ STEP 11: Test Your Site

Visit: `https://yourusername.pythonanywhere.com`

**Test these:**
- ✅ Homepage loads
- ✅ CSS styling works (Tailwind)
- ✅ Login works
- ✅ Chatbot works (if you're a PM/SM user)
- ✅ Can create projects/tasks/events

---

## 🐛 Troubleshooting

### Static Files Not Loading?

1. Check Error log in **Web** tab
2. Verify static files mapping is correct
3. Run `collectstatic` again:
   ```bash
   python manage.py collectstatic --noinput
   ```
4. Check permissions:
   ```bash
   chmod -R 755 ~/edt/staticfiles
   ```

### 500 Internal Server Error?

1. Check **Error log** in Web tab (most important!)
2. Verify all environment variables are set correctly
3. Make sure `PYTHONANYWHERE_HOSTNAME` matches your domain
4. Check that migrations ran successfully

### Tailwind CSS Not Working?

1. Verify `theme/static/css/dist/styles.css` exists
2. If missing, build it:
   ```bash
   cd ~/edt/theme/static_src
   npm install
   npm run build
   ```
   (Note: Requires paid account with Node.js, or build locally and upload)

### Database Errors?

1. Check migrations ran: `python manage.py migrate`
2. Verify database permissions
3. For MySQL: Check `DATABASE_URL` environment variable

---

## 📝 Quick Reference Commands

```bash
# Activate virtual environment
source ~/edt/venv/bin/activate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Check Django version
python manage.py version
```

---

## 🎉 You're Done!

Your application should now be live at `https://yourusername.pythonanywhere.com`

For detailed troubleshooting and advanced configuration, see:
- `PYTHONANYWHERE_DEPLOYMENT.md` - Full deployment guide
- `DEPLOYMENT_CHECKLIST.md` - Complete checklist

---

## 🔄 Updating Your App Later

When you make changes:

1. Pull latest code (if using Git):
   ```bash
   cd ~/edt
   git pull
   ```

2. Activate venv and update:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

3. Reload web app in **Web** tab

---

Good luck with your deployment! 🚀

