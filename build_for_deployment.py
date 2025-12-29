#!/usr/bin/env python
"""
Pre-deployment build script for PythonAnywhere.
This script prepares your Django application for deployment.
"""
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def run_command(command, cwd=None, check=True):
    """Run a shell command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {command}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd or BASE_DIR,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def check_tailwind_build():
    """Check if Tailwind CSS is built"""
    styles_path = BASE_DIR / 'theme' / 'static' / 'css' / 'dist' / 'styles.css'
    if styles_path.exists():
        size = styles_path.stat().st_size
        print(f"✓ Tailwind CSS found ({size:,} bytes)")
        return True
    else:
        print("✗ Tailwind CSS not found")
        return False


def build_tailwind():
    """Build Tailwind CSS"""
    static_src_dir = BASE_DIR / 'theme' / 'static_src'
    
    if not static_src_dir.exists():
        print("✗ theme/static_src directory not found")
        return False
    
    # Check if node_modules exists
    node_modules = static_src_dir / 'node_modules'
    if not node_modules.exists():
        print("Installing npm dependencies...")
        if not run_command("npm install", cwd=static_src_dir):
            return False
    
    # Build Tailwind
    print("Building Tailwind CSS...")
    return run_command("npm run build", cwd=static_src_dir)


def collect_static():
    """Collect Django static files"""
    print("Collecting static files...")
    return run_command("python manage.py collectstatic --noinput")


def check_environment():
    """Check environment variables"""
    print("\nChecking environment variables...")
    
    required_vars = ['SECRET_KEY', 'GEMINI_API_KEY']
    missing = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        print(f"⚠ Warning: Missing environment variables: {', '.join(missing)}")
        print("These should be set on PythonAnywhere:")
        for var in missing:
            print(f"  - {var}")
        return False
    else:
        print("✓ All required environment variables are set")
        return True


def main():
    """Main deployment preparation"""
    print("\n" + "="*60)
    print("PythonAnywhere Deployment Preparation")
    print("="*60)
    
    # Check Python version
    python_version = sys.version_info
    print(f"\nPython version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("⚠ Warning: Python 3.8+ recommended")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if not in_venv:
        print("⚠ Warning: Not in a virtual environment")
        print("Consider activating your virtual environment before deployment")
    
    # Build Tailwind CSS
    if not check_tailwind_build():
        print("\nTailwind CSS needs to be built...")
        if not build_tailwind():
            print("\n✗ Failed to build Tailwind CSS")
            print("You can build it manually:")
            print("  cd theme/static_src")
            print("  npm install")
            print("  npm run build")
            return False
    
    # Collect static files
    if not collect_static():
        print("\n✗ Failed to collect static files")
        return False
    
    # Check environment (optional, just a warning)
    check_environment()
    
    print("\n" + "="*60)
    print("✓ Deployment preparation complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Upload your code to PythonAnywhere")
    print("2. Set environment variables in Web tab")
    print("3. Configure WSGI file")
    print("4. Run migrations: python manage.py migrate")
    print("5. Create superuser: python manage.py createsuperuser")
    print("6. Reload your web app")
    print("\nSee PYTHONANYWHERE_DEPLOYMENT.md for detailed instructions.")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)


