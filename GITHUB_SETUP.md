# How to Commit and Push to a New GitHub Repository

Follow these steps to push your code to a new GitHub repository.

## Step 1: Complete Current Merge (if needed)

You have a merge in progress. Complete it first:

```bash
git commit -m "Complete merge"
```

## Step 2: Create a New GitHub Repository

1. Go to https://github.com/new
2. Enter repository name (e.g., `edt-app` or `django-event-tracker`)
3. Choose **Public** or **Private**
4. **DO NOT** initialize with README, .gitignore, or license (you already have these)
5. Click **Create repository**

## Step 3: Add All Your Files

```bash
# Add all changes (staged and unstaged)
git add .

# Or add specific files if you prefer:
git add .
git add CHATBOT_SETUP.md DEPLOYMENT_CHECKLIST.md DEPLOYMENT_SUMMARY.md
git add HOW_TO_DEPLOY.md PYTHONANYWHERE_DEPLOYMENT.md
git add README_DEPLOYMENT.md build_for_deployment.py
git add pythonanywhere_wsgi.py setup_pythonanywhere.sh
git add chatbot/
```

## Step 4: Commit Your Changes

```bash
git commit -m "Add deployment configuration and chatbot features"
```

Or use a more descriptive message:

```bash
git commit -m "Add PythonAnywhere deployment setup, chatbot integration, and deployment documentation"
```

## Step 5: Change Remote to New Repository

**Option A: Change existing remote URL**

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git
```

Replace:
- `YOUR_USERNAME` with your GitHub username
- `YOUR_NEW_REPO` with your new repository name

**Option B: Add a new remote (if you want to keep both)**

```bash
git remote add new-origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git
```

Then push to the new remote:
```bash
git push -u new-origin main
```

## Step 6: Push to GitHub

```bash
# If you changed the remote URL (Option A):
git push -u origin main

# If you added a new remote (Option B):
git push -u new-origin main
```

The `-u` flag sets up tracking so future pushes are easier.

## Complete Command Sequence

Here's the complete sequence (copy and paste, then edit the repository URL):

```bash
# 1. Complete merge
git commit -m "Complete merge"

# 2. Add all files
git add .

# 3. Commit
git commit -m "Add deployment configuration and chatbot features"

# 4. Change remote (replace with your new repo URL)
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git

# 5. Push to GitHub
git push -u origin main
```

## Troubleshooting

### If you get "remote already exists" error:

```bash
# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git

# Push
git push -u origin main
```

### If you get authentication errors:

**For HTTPS:**
- GitHub now requires a Personal Access Token instead of password
- Create one at: https://github.com/settings/tokens
- Use the token as your password when prompted

**For SSH (recommended):**
```bash
# Change remote to SSH format
git remote set-url origin git@github.com:YOUR_USERNAME/YOUR_NEW_REPO.git

# Push
git push -u origin main
```

### If branch name is different:

If your branch is called `master` instead of `main`:

```bash
git push -u origin master
```

Or rename your branch:
```bash
git branch -M main
git push -u origin main
```

## Verify Your Push

1. Go to your GitHub repository page
2. You should see all your files
3. Check that deployment files are there:
   - `HOW_TO_DEPLOY.md`
   - `PYTHONANYWHERE_DEPLOYMENT.md`
   - `pythonanywhere_wsgi.py`
   - etc.

## Next Steps

After pushing to GitHub, you can:

1. **Deploy to PythonAnywhere** using the new repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git edt
   ```

2. **Add a README.md** to your repository (optional):
   - Create a README.md file describing your project
   - Commit and push it

3. **Set up GitHub Actions** for CI/CD (optional)

---

**Quick Reference:**

```bash
# Complete merge → Add files → Commit → Change remote → Push
git commit -m "Complete merge"
git add .
git commit -m "Add deployment configuration"
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git
git push -u origin main
```

