"""Models for news app."""
from django.db import models
from django.conf import settings
from django.urls import reverse


class Article(models.Model):
    """News article model."""

    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("URL", max_length=200, unique=True)
    content = models.TextField("Содержание")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
        verbose_name="Автор",
    )
    image = models.ImageField(
        "Изображение", upload_to="news/", null=True, blank=True
    )
    published = models.BooleanField("Опубликовано", default=False)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    views = models.IntegerField("Просмотры", default=0)

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug": self.slug})

    def get_approved_comments(self):
        """Get all approved comments."""
        return self.comments.filter(is_approved=True).order_by("-created_at")

    def get_pending_comments(self):
        """Get all pending comments for moderation."""
        return self.comments.filter(is_approved=False).order_by("-created_at")


class Comment(models.Model):
    """Comment model for articles."""

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Статья",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    content = models.TextField("Текст комментария", max_length=1000)
    is_approved = models.BooleanField("Одобрено", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def __str__(self):
        return f"Комментарий от {self.author.username} на {self.article.title}"
