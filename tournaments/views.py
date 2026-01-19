"""Views for tournaments app."""

from typing import Any
import random
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q, Count, Case, When, IntegerField
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from loguru import logger

from .models import (
    Tournament,
    Match,
    Participant,
    CourtLocation,
    PartnerSearch,
    Rating,
    Referral,
)

try:
    from news.models import Article
except ImportError:
    Article = None


# Настройки системы рейтинга
# Эти значения можно изменить для настройки баланса системы
RATING_POINTS_WIN = 25      # Очки за победу в матче
RATING_POINTS_LOSS = -10    # Очки за поражение (отрицательное значение)
RATING_POINTS_MIN = 0       # Минимальный рейтинг (не может быть меньше)


class HomeView(ListView):
    """Home page view with upcoming tournaments and statistics."""

    model = Tournament
    template_name = "tournaments/home.html"
    context_object_name = "tournaments"
    paginate_by = 9

    def get_queryset(self):
        from datetime import date
        today = date.today()
        
        # Показываем только турниры, которые еще не завершились
        # И только те, что начинаются не позже чем через 2 месяца
        queryset = Tournament.objects.filter(
            Q(status="UPCOMING", start_date__gte=today) |
            Q(status="ONGOING", start_date__lte=today, end_date__gte=today)
        ).filter(end_date__gte=today)

        # Фильтрация по параметрам
        category = self.request.GET.get("category")
        level = self.request.GET.get("level")
        region = self.request.GET.get("region")
        tournament_type = self.request.GET.get("type")

        if category:
            queryset = queryset.filter(category=category)
        if level:
            queryset = queryset.filter(level=level)
        if region:
            queryset = queryset.filter(region=region)
        if tournament_type:
            queryset = queryset.filter(tournament_type=tournament_type)

        return queryset.order_by("start_date")

    def get_context_data(self, **kwargs):
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        context = super().get_context_data(**kwargs)
        
        # Последние завершенные матчи с выборкой связанных объектов
        context["recent_matches"] = Match.objects.filter(
            status="FINISHED"
        ).select_related(
            "tournament", "player1", "player2", "winner"
        ).order_by("-updated_at")[:5]
        
        # Топ игроков по рейтингу
        context["top_players"] = Rating.objects.select_related("user").order_by(
            "rank_position"
        )[:10]
        
        # Общая статистика
        context["stats"] = {
            "total_tournaments": Tournament.objects.count(),
            "active_tournaments": Tournament.objects.filter(
                status__in=["UPCOMING", "ONGOING"]
            ).count(),
            "total_players": User.objects.filter(is_active=True).count(),
            "total_matches": Match.objects.filter(status="FINISHED").count(),
        }
        
        # Выбор для фильтров
        context["category_choices"] = Tournament.CATEGORY_CHOICES
        context["level_choices"] = Tournament.LEVEL_CHOICES
        context["region_choices"] = Tournament.REGION_CHOICES
        context["type_choices"] = Tournament.TYPE_CHOICES
        
        # Последние новости
        if Article:
            context["recent_articles"] = Article.objects.filter(
                published=True
            ).order_by("-created_at")[:3]
        
        return context


class TournamentListView(ListView):
    """View for listing all tournaments."""

    model = Tournament
    template_name = "tournaments/tournament_list.html"
    context_object_name = "tournaments"
    paginate_by = 10

    def get_queryset(self):
        queryset = Tournament.objects.all()
        category = self.request.GET.get("category")
        status = self.request.GET.get("status")

        if category:
            queryset = queryset.filter(category=category)
        if status:
            queryset = queryset.filter(status=status)

        return queryset


class TournamentDetailView(DetailView):
    """View for tournament details with bracket and draw logic."""

    model = Tournament
    template_name = "tournaments/tournament_detail.html"
    context_object_name = "tournament"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tournament = self.object

        participants = tournament.participants.select_related("user").order_by(
            "seed", "registered_at"
        )
        matches = tournament.matches.select_related(
            "player1", "player2", "winner"
        ).order_by("round", "scheduled_date")

        # Подсчет статистики
        total_participants = participants.count()
        matches_played = matches.filter(status="FINISHED").count()
        matches_scheduled = matches.filter(status="SCHEDULED").count()

        # Группировка матчей по раундам
        rounds_data = {}
        for match in matches:
            round_name = match.round or "Без раунда"
            if round_name not in rounds_data:
                rounds_data[round_name] = []
            rounds_data[round_name].append(match)

        # Определение текущего раунда
        current_round = None
        if matches_scheduled > 0:
            current_round = matches.filter(status="SCHEDULED").first().round

        context.update(
            {
                "participants": participants,
                "matches": matches,
                "total_participants": total_participants,
                "matches_played": matches_played,
                "matches_scheduled": matches_scheduled,
                "rounds_data": rounds_data,
                "current_round": current_round,
                "can_draw": total_participants >= 8 and matches.count() == 0,
            }
        )

        return context


@login_required
def register_for_tournament(request, pk: int):
    """Register user for tournament."""
    tournament = get_object_or_404(Tournament, pk=pk)

    if tournament.participants.count() >= tournament.max_participants:
        messages.warning(request, "Турнир заполнен")
        return redirect("tournament_detail", pk=pk)

    Participant.objects.get_or_create(tournament=tournament, user=request.user)
    messages.success(request, "Вы успешно зарегистрированы на турнир!")

    return redirect("tournament_detail", pk=pk)


@login_required
def generate_draw(request, pk: int):
    """Generate tournament draw (жеребьевка) for Olympic system."""
    if not request.user.is_staff:
        messages.error(request, "Недостаточно прав")
        return redirect("tournament_detail", pk=pk)

    tournament = get_object_or_404(Tournament, pk=pk)
    participants = list(tournament.participants.select_related("user"))

    if len(participants) < 8:
        messages.error(request, "Недостаточно участников (минимум 8)")
        return redirect("tournament_detail", pk=pk)

    if tournament.matches.exists():
        messages.error(request, "Жеребьевка уже проведена")
        return redirect("tournament_detail", pk=pk)

    # Перемешать участников (без посева делаем случайную жеребьевку)
    random.shuffle(participants)

    # Создать матчи первого раунда
    round_name = "1/4 финала" if len(participants) == 8 else "1/8 финала"
    matches_created = 0

    for i in range(0, len(participants), 2):
        if i + 1 < len(participants):
            Match.objects.create(
                tournament=tournament,
                player1=participants[i].user,
                player2=participants[i + 1].user,
                round=round_name,
                status="SCHEDULED",
            )
            matches_created += 1

    logger.info(
        f"Draw generated for tournament {tournament.id}: {matches_created} matches created"
    )
    messages.success(
        request, f"Жеребьевка проведена! Создано матчей: {matches_created}"
    )

    return redirect("tournament_detail", pk=pk)


class MatchListView(ListView):
    """View for listing matches."""

    model = Match
    template_name = "tournaments/match_list.html"
    context_object_name = "matches"
    paginate_by = 20

    def get_queryset(self):
        queryset = Match.objects.select_related(
            "tournament",
            "player1",
            "player2",
            "winner",
            "court_location",
        )

        # Фильтрация
        tournament_id = self.request.GET.get("tournament")
        status = self.request.GET.get("status")
        round_name = self.request.GET.get("round")
        player = self.request.GET.get("player")

        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        if status:
            queryset = queryset.filter(status=status)
        if round_name:
            queryset = queryset.filter(round=round_name)
        if player:
            queryset = queryset.filter(
                Q(player1__username__icontains=player)
                | Q(player1__first_name__icontains=player)
                | Q(player1__last_name__icontains=player)
                | Q(player2__username__icontains=player)
                | Q(player2__first_name__icontains=player)
                | Q(player2__last_name__icontains=player)
            )

        return queryset.order_by("-scheduled_date", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Все турниры для фильтра
        context["tournaments"] = Tournament.objects.all().order_by("-start_date")
        return context


class MatchDetailView(DetailView):
    """View for match details."""

    model = Match
    template_name = "tournaments/match_detail.html"
    context_object_name = "match"


# Новые views для функционала tennis-play.com


class CourtLocationListView(ListView):
    """View for listing court locations."""

    model = CourtLocation
    template_name = "tournaments/court_list.html"
    context_object_name = "courts"
    paginate_by = 12

    def get_queryset(self):
        queryset = CourtLocation.objects.filter(is_active=True)

        # Фильтрация
        region = self.request.GET.get("region")
        city = self.request.GET.get("city")
        max_cost = self.request.GET.get("max_cost")

        if region:
            queryset = queryset.filter(region=region)
        if city:
            queryset = queryset.filter(city__icontains=city)
        if max_cost:
            try:
                queryset = queryset.filter(cost_per_hour__lte=float(max_cost))
            except ValueError:
                pass

        return queryset.order_by("cost_per_hour")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["region_choices"] = CourtLocation.REGION_CHOICES
        return context


class CourtLocationDetailView(DetailView):
    """View for court location details."""

    model = CourtLocation
    template_name = "tournaments/court_detail.html"
    context_object_name = "court"


class PartnerSearchListView(ListView):
    """View for listing partner search requests with filters."""

    model = PartnerSearch
    template_name = "tournaments/partner_search_list.html"
    context_object_name = "searches"
    paginate_by = 20

    def get_queryset(self):
        queryset = PartnerSearch.objects.filter(is_active=True).select_related(
            "user", "user__player_rating"
        )

        # Фильтрация
        sport_type = self.request.GET.get("sport")
        skill_level = self.request.GET.get("level")
        city = self.request.GET.get("city")

        if sport_type:
            queryset = queryset.filter(sport_type=sport_type)
        if skill_level:
            queryset = queryset.filter(skill_level=skill_level)
        if city:
            queryset = queryset.filter(user__city__icontains=city)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sport_choices"] = PartnerSearch.SPORT_CHOICES
        context["level_choices"] = PartnerSearch.LEVEL_CHOICES
        return context


class PartnerSearchCreateView(CreateView):
    """View for creating partner search request."""

    model = PartnerSearch
    template_name = "tournaments/partner_search_create.html"
    fields = [
        "sport_type",
        "skill_level",
        "preferred_time",
        "preferred_location",
        "contact_info",
    ]
    success_url = reverse_lazy("partner_search_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Деактивировать предыдущие заявки пользователя для этого вида спорта
        PartnerSearch.objects.filter(
            user=self.request.user, sport_type=form.instance.sport_type, is_active=True
        ).update(is_active=False)
        messages.success(self.request, "Заявка на поиск партнера успешно создана!")
        return super().form_valid(form)


class RatingListView(ListView):
    """View for player ratings."""

    model = Rating
    template_name = "tournaments/rating_list.html"
    context_object_name = "ratings"
    paginate_by = 50

    def get_queryset(self):
        queryset = Rating.objects.select_related("user").all()

        # Фильтрация
        gender = self.request.GET.get("gender")
        ntrp_level = self.request.GET.get("level")
        city = self.request.GET.get("city")
        min_matches = self.request.GET.get("min_matches")

        if gender:
            queryset = queryset.filter(user__gender=gender)
        if ntrp_level:
            queryset = queryset.filter(ntrp_level=ntrp_level)
        if city:
            queryset = queryset.filter(user__city__icontains=city)
        if min_matches:
            try:
                queryset = queryset.filter(matches_played__gte=int(min_matches))
            except ValueError:
                pass

        return queryset.order_by("-points", "rank_position")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Топ-10 игроков для графика
        context["top_10_players"] = Rating.objects.select_related("user").order_by(
            "-points"
        )[:10]
        return context


@login_required
def my_games_view(request):
    """Personal dashboard for player."""
    user = request.user

    # Активные турниры
    active_tournaments = Tournament.objects.filter(
        participants__user=user, status__in=["UPCOMING", "ONGOING"]
    ).distinct()

    # Предстоящие матчи
    upcoming_matches = (
        Match.objects.filter(Q(player1=user) | Q(player2=user), status="SCHEDULED")
        .select_related("tournament", "player1", "player2", "court_location")
        .order_by("scheduled_date")
    )

    # Ожидающие подтверждения результата
    pending_confirmation = Match.objects.filter(
        Q(player1=user, score_confirmed_by_player1=False)
        | Q(player2=user, score_confirmed_by_player2=False),
        status="FINISHED",
        player1_set1__isnull=False,
    ).select_related("tournament", "player1", "player2")

    # История игр
    match_history = (
        Match.objects.filter(
            Q(player1=user) | Q(player2=user),
            status="FINISHED",
            score_confirmed_by_player1=True,
            score_confirmed_by_player2=True,
        )
        .select_related("tournament", "player1", "player2", "winner")
        .order_by("-actual_date", "-updated_at")[:10]
    )

    # Рейтинг
    try:
        rating = Rating.objects.get(user=user)
    except Rating.DoesNotExist:
        rating = None

    # Реферальная статистика
    referrals = Referral.objects.filter(referrer=user).select_related(
        "referred", "tournament"
    )
    total_bonus = sum(r.bonus_amount for r in referrals if r.status == "PAID")

    context = {
        "active_tournaments": active_tournaments,
        "upcoming_matches": upcoming_matches,
        "pending_confirmation": pending_confirmation,
        "match_history": match_history,
        "rating": rating,
        "referrals": referrals,
        "total_bonus": total_bonus,
    }

    return render(request, "tournaments/my_games.html", context)


@login_required
def submit_match_result(request, pk):
    """Submit match result."""
    match = get_object_or_404(Match, pk=pk)
    user = request.user

    # Проверка, что пользователь участвует в матче
    if user not in [match.player1, match.player2]:
        messages.error(request, "Вы не участвуете в этом матче.")
        return redirect("my_games")

    if request.method == "POST":
        try:
            # Получение данных из формы
            p1_set1 = int(request.POST.get("player1_set1", 0))
            p1_set2 = int(request.POST.get("player1_set2", 0))
            p1_set3 = (
                int(request.POST.get("player1_set3", 0))
                if request.POST.get("player1_set3")
                else None
            )

            p2_set1 = int(request.POST.get("player2_set1", 0))
            p2_set2 = int(request.POST.get("player2_set2", 0))
            p2_set3 = (
                int(request.POST.get("player2_set3", 0))
                if request.POST.get("player2_set3")
                else None
            )

            # Обновление счета
            match.player1_set1 = p1_set1
            match.player1_set2 = p1_set2
            match.player1_set3 = p1_set3
            match.player2_set1 = p2_set1
            match.player2_set2 = p2_set2
            match.player2_set3 = p2_set3

            # ═══════════════════════════════════════════════════════════
            # ОПРЕДЕЛЕНИЕ ПОБЕДИТЕЛЯ ПО СИСТЕМЕ ТЕННИСА
            # ═══════════════════════════════════════════════════════════
            # Правило: Победитель - тот, кто выиграл БОЛЬШИНСТВО сетов
            # 
            # Примеры:
            # - Игрок 1: 6-3, 4-6, 6-2 → выиграл 2 сета из 3 → ПОБЕДИТЕЛЬ
            # - Игрок 2: 3-6, 6-4, 2-6 → выиграл 1 сет из 3 → проигравший
            # ═══════════════════════════════════════════════════════════
            
            p1_sets = 0  # Количество сетов, выигранных игроком 1
            p2_sets = 0  # Количество сетов, выигранных игроком 2

            # Проверка 1-го сета
            if p1_set1 > p2_set1:
                p1_sets += 1  # Игрок 1 выиграл сет
            else:
                p2_sets += 1  # Игрок 2 выиграл сет

            # Проверка 2-го сета
            if p1_set2 > p2_set2:
                p1_sets += 1
            else:
                p2_sets += 1

            # Проверка 3-го сета (если был сыгран)
            if p1_set3 is not None and p2_set3 is not None:
                if p1_set3 > p2_set3:
                    p1_sets += 1
                else:
                    p2_sets += 1

            # Определить победителя: кто выиграл больше сетов
            match.winner = match.player1 if p1_sets > p2_sets else match.player2
            
            # Логирование результата для отладки
            logger.info(
                f"Матч {match.pk}: {match.player1.username} ({p1_sets} sets) vs "
                f"{match.player2.username} ({p2_sets} sets) → Победитель: {match.winner.username}"
            )

            # Подтверждение от игрока
            if user == match.player1:
                match.score_confirmed_by_player1 = True
            else:
                match.score_confirmed_by_player2 = True

            match.status = "FINISHED"
            match.actual_date = timezone.now()
            match.save()

            # Если оба подтвердили - обновить рейтинг
            if match.is_score_confirmed():
                update_player_ratings(match)
                messages.success(
                    request, "Результат подтвержден обоими игроками. Рейтинг обновлен!"
                )
            else:
                messages.success(
                    request, "Результат сохранен. Ожидается подтверждение от соперника."
                )

            return redirect("my_games")

        except (ValueError, TypeError) as e:
            messages.error(request, f"Ошибка при сохранении результата: {e}")

    context = {"match": match}
    return render(request, "tournaments/match_submit_result.html", context)


def update_player_ratings(match):
    """
    Update player ratings after match completion.
    
    Логика начисления очков:
    - Победитель получает: +25 очков (RATING_POINTS_WIN)
    - Проигравший теряет: -10 очков (RATING_POINTS_LOSS)
    - Минимальный рейтинг: 0 очков (не может быть отрицательным)
    
    Args:
        match: Объект матча с определенным победителем
    """
    # Получить или создать рейтинг для обоих игроков
    p1_rating, created1 = Rating.objects.get_or_create(
        user=match.player1,
        defaults={'points': 1000}  # Начальный рейтинг для новых игроков
    )
    p2_rating, created2 = Rating.objects.get_or_create(
        user=match.player2,
        defaults={'points': 1000}
    )

    # Обновить статистику матчей
    p1_rating.matches_played += 1
    p2_rating.matches_played += 1

    # Определить победителя и начислить очки
    if match.winner == match.player1:
        # Игрок 1 победил
        p1_rating.matches_won += 1
        p1_rating.points += RATING_POINTS_WIN  # +25 очков победителю
        p2_rating.points = max(
            p2_rating.points + RATING_POINTS_LOSS,  # -10 очков проигравшему
            RATING_POINTS_MIN  # Но не меньше 0
        )
        logger.info(
            f"Рейтинг обновлен: {match.player1.username} +{RATING_POINTS_WIN}, "
            f"{match.player2.username} {RATING_POINTS_LOSS}"
        )
    else:
        # Игрок 2 победил
        p2_rating.matches_won += 1
        p2_rating.points += RATING_POINTS_WIN
        p1_rating.points = max(
            p1_rating.points + RATING_POINTS_LOSS,
            RATING_POINTS_MIN
        )
        logger.info(
            f"Рейтинг обновлен: {match.player2.username} +{RATING_POINTS_WIN}, "
            f"{match.player1.username} {RATING_POINTS_LOSS}"
        )

    # Сохранить изменения
    p1_rating.save()
    p2_rating.save()

    # Пересчитать позиции в общем рейтинге
    recalculate_rankings()


def recalculate_rankings():
    """Recalculate rank positions for all players."""
    ratings = Rating.objects.all().order_by("-points")
    for index, rating in enumerate(ratings, start=1):
        rating.rank_position = index
        rating.save(update_fields=["rank_position"])


@login_required
def admin_dashboard(request):
    """Admin dashboard with statistics and management tools."""
    from django.contrib.auth import get_user_model
    import django
    import sys
    from django.conf import settings
    from datetime import timedelta
    
    User = get_user_model()
    
    # Проверка прав администратора
    if not request.user.is_staff:
        messages.error(request, "У вас нет доступа к админ панели")
        return redirect("home")
    
    # Общая статистика
    stats = {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "total_tournaments": Tournament.objects.count(),
        "active_tournaments": Tournament.objects.filter(
            status__in=["UPCOMING", "ONGOING"]
        ).count(),
        "total_matches": Match.objects.count(),
        "finished_matches": Match.objects.filter(status="FINISHED").count(),
        "total_courts": CourtLocation.objects.count(),
        "active_courts": CourtLocation.objects.filter(is_active=True).count(),
    }
    
    # Активность за неделю
    week_ago = timezone.now() - timedelta(days=7)
    stats["matches_this_week"] = Match.objects.filter(
        created_at__gte=week_ago
    ).count()
    stats["new_users_this_week"] = User.objects.filter(
        date_joined__gte=week_ago
    ).count()
    stats["active_partner_searches"] = PartnerSearch.objects.filter(
        is_active=True
    ).count()
    
    # Матчи, ожидающие подтверждения (где хотя бы один игрок не подтвердил счет)
    pending_confirmations = Match.objects.filter(
        status="IN_PROGRESS"
    ).exclude(
        score_confirmed_by_player1=True,
        score_confirmed_by_player2=True
    ).select_related("tournament", "player1", "player2")[:10]
    
    # Последние турниры
    recent_tournaments = (
        Tournament.objects.all()
        .prefetch_related("participants")
        .order_by("-created_at")[:10]
    )
    
    # Последние пользователи
    recent_users = User.objects.filter(is_active=True).order_by("-date_joined")[:10]
    
    # Системная информация
    django_version = django.get_version()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    db_name = settings.DATABASES["default"]["ENGINE"].split(".")[-1]
    
    context = {
        "stats": stats,
        "pending_confirmations": pending_confirmations,
        "recent_tournaments": recent_tournaments,
        "recent_users": recent_users,
        "django_version": django_version,
        "python_version": python_version,
        "db_name": db_name,
    }
    
    return render(request, "tournaments/admin_dashboard.html", context)
