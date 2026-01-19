"""Tournaments app configuration."""
from django.apps import AppConfig


class TournamentsConfig(AppConfig):
    """Configuration for tournaments app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "tournaments"
    verbose_name = "Турниры"
