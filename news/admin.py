"""Admin configuration for news app."""
from django.contrib import admin
from .models import Article, Comment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin interface for Article model."""

    list_display = ["title", "author", "published", "created_at", "views"]
    list_filter = ["published", "created_at", "author"]
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    fieldsets = [
        (
            "Основная информация",
            {"fields": ("title", "slug", "author", "content", "image")},
        ),
        ("Публикация", {"fields": ("published",)}),
    ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model."""

    list_display = ["author", "article", "is_approved", "created_at"]
    list_filter = ["is_approved", "created_at", "article"]
    search_fields = ["content", "author__username", "article__title"]
    readonly_fields = ["author", "article", "created_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    fieldsets = [
        ("Информация о комментарии", {"fields": ("article", "author")}),
        ("Содержание", {"fields": ("content",)}),
        ("Модерация", {"fields": ("is_approved",)}),
        ("Даты", {"fields": ("created_at",), "classes": ("collapse",)}),
    ]
