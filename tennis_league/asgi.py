"""ASGI config for tennis_league project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tennis_league.settings")

application = get_asgi_application()
