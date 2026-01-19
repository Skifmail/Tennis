"""Forms for news app."""
from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    """Form for adding comments to articles."""

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Напишите ваш комментарий...",
                }
            )
        }
        labels = {"content": ""}
