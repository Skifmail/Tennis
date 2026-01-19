"""Forms for user registration and profile editing."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
        label="Email",
    )
    
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+7-900-123-45-67"}),
        label="Телефон",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["class"] = "form-control"


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""
    
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
        label="Дата рождения",
    )
    
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Расскажите о себе, вашем опыте в теннисе...",
            }
        ),
        label="О себе",
    )
    
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "accept": "image/*",
            }
        ),
        label="Фото профиля",
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "birth_date",
            "gender",
            "city",
            "photo",
            "bio",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Имя"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Фамилия"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "email@example.com"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+7 (999) 123-45-67"}
            ),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Москва"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем help_text для некоторых полей
        self.fields["phone"].help_text = "Контактный телефон для связи"
        self.fields["city"].help_text = "Ваш город проживания"
        self.fields["birth_date"].help_text = "Для расчета возрастной категории"
        self.fields["photo"].help_text = "JPG, PNG до 5МБ"
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.FileInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
