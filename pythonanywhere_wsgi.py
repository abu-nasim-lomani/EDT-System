# +++++++++++ DJANGO +++++++++++
# To use your own Django app use code like this:
import os
import sys

# Assuming your Django project is in ~/edt
# Adjust the path if your project is located elsewhere
path = '/home/yourusername/edt'  # CHANGE THIS to your actual path
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Then:
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


