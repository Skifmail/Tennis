"""News app configuration."""
from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Configuration for news app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "news"
    verbose_name = "Новости"
