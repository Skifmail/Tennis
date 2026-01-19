"""URL patterns for accounts app."""
from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    UserProfileEditView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("profile/", UserProfileView.as_view(), name="my_profile"),
    path("profile/edit/", UserProfileEditView.as_view(), name="profile_edit"),
    path("profile/<str:username>/", UserProfileView.as_view(), name="profile"),
]
