"""URL patterns for tournaments app."""
from django.urls import path
from .views import (
    HomeView,
    TournamentListView,
    TournamentDetailView,
    MatchListView,
    MatchDetailView,
    register_for_tournament,
    generate_draw,
    CourtLocationListView,
    CourtLocationDetailView,
    PartnerSearchListView,
    PartnerSearchCreateView,
    RatingListView,
    my_games_view,
    submit_match_result,
    admin_dashboard,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("tournaments/", TournamentListView.as_view(), name="tournament_list"),
    path(
        "tournaments/<int:pk>/", TournamentDetailView.as_view(), name="tournament_detail"
    ),
    path(
        "tournaments/<int:pk>/register/",
        register_for_tournament,
        name="tournament_register",
    ),
    path(
        "tournaments/<int:pk>/draw/",
        generate_draw,
        name="tournament_draw",
    ),
    path("matches/", MatchListView.as_view(), name="match_list"),
    path("matches/<int:pk>/", MatchDetailView.as_view(), name="match_detail"),
    path("matches/<int:pk>/submit-result/", submit_match_result, name="match_submit_result"),
    
    # Корты
    path("courts/", CourtLocationListView.as_view(), name="court_list"),
    path("courts/<int:pk>/", CourtLocationDetailView.as_view(), name="court_detail"),
    
    # Поиск партнера
    path("partner-search/", PartnerSearchListView.as_view(), name="partner_search_list"),
    path("partner-search/create/", PartnerSearchCreateView.as_view(), name="partner_search_create"),
    
    # Рейтинг
    path("rating/", RatingListView.as_view(), name="rating_list"),
    
    # Личный кабинет
    path("my-games/", my_games_view, name="my_games"),
    
    # Админ панель
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
]
