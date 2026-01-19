"""Admin configuration for accounts app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""

    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "gender",
        "rating",
        "is_staff",
    ]
    list_filter = ["is_staff", "is_active", "gender", "city"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["-rating", "username"]

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Дополнительная информация",
            {
                "fields": (
                    "phone",
                    "birth_date",
                    "gender",
                    "city",
                    "photo",
                    "rating",
                    "bio",
                )
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Дополнительная информация",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone",
                    "birth_date",
                    "gender",
                    "city",
                )
            },
        ),
    )
