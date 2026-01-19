"""WSGI config for tennis_league project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tennis_league.settings")

application = get_wsgi_application()
