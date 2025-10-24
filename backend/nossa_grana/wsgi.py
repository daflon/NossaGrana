"""
WSGI config for nossa_grana project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')

application = get_wsgi_application()