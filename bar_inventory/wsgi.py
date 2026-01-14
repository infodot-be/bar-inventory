"""
WSGI config for bar_inventory project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bar_inventory.settings')

application = get_wsgi_application()
