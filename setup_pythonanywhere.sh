#!/bin/bash
# PythonAnywhere Quick Setup Script
# Run this script in your PythonAnywhere Bash console after uploading your code

set -e  # Exit on error

echo "=========================================="
echo "PythonAnywhere Setup Script"
echo "=========================================="

# Get the current directory (should be ~/edt)
PROJECT_DIR=$(pwd)
echo "Project directory: $PROJECT_DIR"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from your project root directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3.10 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing requirements..."
pip install -r requirements.txt

# Check if Tailwind needs to be built
if [ -d "theme/static_src" ]; then
    echo ""
    echo "Checking Tailwind CSS..."
    if [ ! -f "theme/static/css/dist/styles.css" ]; then
        echo "Tailwind CSS not found. Checking for Node.js..."
        if command -v node &> /dev/null; then
            echo "Building Tailwind CSS..."
            cd theme/static_src
            npm install
            npm run build
            cd ../..
        else
            echo "Warning: Node.js not found. Tailwind CSS must be built locally or uploaded."
            echo "Please build it locally and upload the compiled CSS file."
        fi
    else
        echo "Tailwind CSS already built"
    fi
fi

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo ""
echo "Running migrations..."
python manage.py migrate

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Set environment variables in Web tab:"
echo "   - SECRET_KEY"
echo "   - DEBUG=False"
echo "   - GEMINI_API_KEY"
echo "   - PYTHONANYWHERE_HOSTNAME=yourusername.pythonanywhere.com"
echo ""
echo "2. Configure WSGI file (use pythonanywhere_wsgi.py as template)"
echo ""
echo "3. Configure static files mapping:"
echo "   URL: /static/"
echo "   Directory: $PROJECT_DIR/staticfiles"
echo ""
echo "4. Create superuser:"
echo "   python manage.py createsuperuser"
echo ""
echo "5. Reload your web app in the Web tab"
echo ""
echo "See PYTHONANYWHERE_DEPLOYMENT.md for detailed instructions."


