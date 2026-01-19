"""URL маршруты для информационных страниц."""
from django.urls import path
from .views import (
    RatingHubView,
    RatingSystemView,
    TournamentSystemsView,
    NTRPRatingView,
    RatingLevelsView,
    PointsCalculationView,
)

app_name = "info"

urlpatterns = [
    path("", RatingHubView.as_view(), name="hub"),
    path("rating/", RatingSystemView.as_view(), name="rating_system"),
    path("tournaments/", TournamentSystemsView.as_view(), name="tournament_systems"),
    path("ntrp/", NTRPRatingView.as_view(), name="ntrp"),
    path("levels/", RatingLevelsView.as_view(), name="levels"),
    path("points/", PointsCalculationView.as_view(), name="points"),
]
