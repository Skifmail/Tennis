"""User models for tennis league."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with additional fields."""

    GENDER_CHOICES = [
        ("M", "Мужской"),
        ("F", "Женский"),
    ]

    phone = models.CharField("Телефон", max_length=20, blank=True)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    gender = models.CharField("Пол", max_length=1, choices=GENDER_CHOICES, blank=True)
    city = models.CharField("Город", max_length=100, blank=True)
    photo = models.ImageField(
        "Фото", upload_to="users/photos/", null=True, blank=True
    )
    rating = models.IntegerField("Рейтинг", default=1000)
    bio = models.TextField("О себе", blank=True)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-rating", "username"]

    def __str__(self):
        return self.get_full_name() or self.username
