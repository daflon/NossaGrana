"""
ASGI config for nossa_grana project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')

application = get_asgi_application()