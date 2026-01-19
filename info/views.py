"""Views для информационных страниц."""
from django.views.generic import TemplateView


class RatingSystemView(TemplateView):
    """Страница с объяснением рейтинговой системы."""
    template_name = "info/rating_system.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Система рейтинга'
        return context


class TournamentSystemsView(TemplateView):
    """Страница с объяснением систем турниров."""
    template_name = "info/tournament_systems.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Системы турниров'
        return context


class NTRPRatingView(TemplateView):
    """Страница с объяснением NTRP рейтинга."""
    template_name = "info/ntrp_rating.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'NTRP рейтинг'
        return context


class RatingLevelsView(TemplateView):
    """Страница с описанием уровней рейтинга."""
    template_name = "info/rating_levels.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Уровни рейтинга'
        return context


class PointsCalculationView(TemplateView):
    """Страница с объяснением расчёта очков."""
    template_name = "info/points_calculation.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Расчёт очков'
        return context


class RatingHubView(TemplateView):
    """Главная страница информации о рейтингах."""
    template_name = "info/rating_hub.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Справочный центр - Рейтинги'
        return context
