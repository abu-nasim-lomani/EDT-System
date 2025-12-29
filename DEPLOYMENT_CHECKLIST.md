# PythonAnywhere Deployment Checklist

Use this checklist to ensure a smooth deployment process.

## Pre-Deployment (Local)

- [ ] **Code is committed to Git**
  - All changes committed
  - `.env` file is NOT committed (in .gitignore)
  - `db.sqlite3` is NOT committed (in .gitignore)

- [ ] **Tailwind CSS is built**
  ```bash
  cd theme/static_src
  npm install
  npm run build
  ```
  - Verify `theme/static/css/dist/styles.css` exists and is recent

- [ ] **Run pre-deployment script** (optional)
  ```bash
  python build_for_deployment.py
  ```

- [ ] **Test locally**
  - Application runs without errors
  - All features work correctly
  - Static files load properly

- [ ] **Prepare environment variables**
  - Generate new SECRET_KEY for production
  - Have GEMINI_API_KEY ready
  - Note your PythonAnywhere username

## Deployment (PythonAnywhere)

### Initial Setup

- [ ] **Create PythonAnywhere account**
  - Sign up at https://www.pythonanywhere.com
  - Note your username

- [ ] **Upload code**
  - [ ] Option A: Clone via Git
    ```bash
    cd ~
    git clone <your-repo-url> edt
    ```
  - [ ] Option B: Upload files via Files tab

- [ ] **Set up virtual environment**
  ```bash
  cd ~/edt
  python3.10 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

- [ ] **Configure environment variables**
  - Go to Web tab → Web app → Environment variables
  - [ ] `SECRET_KEY` = (generated production key)
  - [ ] `DEBUG` = `False`
  - [ ] `GEMINI_API_KEY` = (your API key)
  - [ ] `GEMINI_MODEL` = `gemini-2.5-pro` (optional)
  - [ ] `PYTHONANYWHERE_HOSTNAME` = `yourusername.pythonanywhere.com`

### Database Setup

- [ ] **Set up database**
  - [ ] Free account: SQLite (default)
  - [ ] Paid account: MySQL
    - Create database in Databases tab
    - Set `DATABASE_URL` environment variable

- [ ] **Run migrations**
  ```bash
  cd ~/edt
  source venv/bin/activate
  python manage.py migrate
  ```

- [ ] **Create superuser**
  ```bash
  python manage.py createsuperuser
  ```

### Static Files

- [ ] **Build Tailwind CSS** (if paid account with Node.js)
  ```bash
  cd ~/edt/theme/static_src
  npm install
  npm run build
  ```
  OR ensure pre-built CSS is uploaded

- [ ] **Collect static files**
  ```bash
  cd ~/edt
  source venv/bin/activate
  python manage.py collectstatic --noinput
  ```

- [ ] **Configure static files mapping**
  - Web tab → Static files
  - URL: `/static/`
  - Directory: `/home/yourusername/edt/staticfiles/`

### WSGI Configuration

- [ ] **Configure WSGI file**
  - Web tab → WSGI configuration file
  - Update path in `pythonanywhere_wsgi.py`
  - Copy content to PythonAnywhere WSGI file
  - Save

- [ ] **Reload web app**
  - Click green "Reload" button

## Post-Deployment Verification

- [ ] **Test homepage**
  - Visit `https://yourusername.pythonanywhere.com`
  - Page loads without errors

- [ ] **Test authentication**
  - [ ] Login works
  - [ ] Logout works
  - [ ] Can access protected pages

- [ ] **Test static files**
  - [ ] CSS styles load correctly
  - [ ] JavaScript files load
  - [ ] Images display properly

- [ ] **Test chatbot**
  - [ ] Chatbot widget appears (for PM/SM users)
  - [ ] Can send messages
  - [ ] Receives responses (if Gemini API configured)

- [ ] **Test core features**
  - [ ] Projects list/creation
  - [ ] Tasks list/creation
  - [ ] Events list/creation
  - [ ] Dashboard displays correctly

- [ ] **Check error logs**
  - Web tab → Error log
  - No critical errors

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set (not default)
- [ ] `.env` file not accessible via web
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] HTTPS enabled (automatic on PythonAnywhere)
- [ ] API keys in environment variables only
- [ ] Database credentials secure

## Troubleshooting

If something doesn't work:

1. **Check Error Log**
   - Web tab → Error log
   - Look for Python tracebacks

2. **Check Server Log**
   - Web tab → Server log
   - Look for startup messages

3. **Verify Environment Variables**
   - Web tab → Environment variables
   - Ensure all required vars are set

4. **Check File Permissions**
   ```bash
   chmod -R 755 ~/edt/staticfiles
   ```

5. **Verify Static Files**
   - Ensure `collectstatic` was run
   - Check static files mapping

6. **Test Database Connection**
   ```bash
   python manage.py dbshell
   ```

## Maintenance

- [ ] **Set up backups** (optional)
  - Database backups
  - Code backups via Git

- [ ] **Monitor usage**
  - Check PythonAnywhere dashboard
  - Monitor API usage (Gemini)

- [ ] **Update regularly**
  - Pull latest code changes
  - Update dependencies
  - Run migrations as needed

## Quick Reference Commands

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

# Run Django shell
python manage.py shell
```

## Support Resources

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Django Deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
- WhiteNoise Docs: http://whitenoise.evans.io/
- Project Documentation: See `PYTHONANYWHERE_DEPLOYMENT.md`


