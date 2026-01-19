"""Views for user authentication and profile management."""

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Sum

from tournaments.models import Tournament, Match, Rating, Participant, RatingHistory
from .forms import UserRegistrationForm, UserProfileForm
from .models import User


class UserRegistrationView(CreateView):
    """View for user registration."""

    model = User
    form_class = UserRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class UserLoginView(LoginView):
    """View for user login."""

    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    """View for user logout."""

    next_page = reverse_lazy("home")


class UserProfileView(LoginRequiredMixin, DetailView):
    """View for displaying user profile."""

    model = User
    template_name = "accounts/profile.html"
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        if username:
            return User.objects.get(username=username)
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        # Статистика участника
        participants = Participant.objects.filter(user=user)
        tournaments_count = participants.count()

        # Статистика матчей
        matches = Match.objects.filter(Q(player1=user) | Q(player2=user))

        wins = 0
        losses = 0
        for match in matches:
            if match.winner == user:
                wins += 1
            elif match.status == "FINISHED":
                losses += 1

        total_matches = matches.filter(status="FINISHED").count()
        win_percentage = (wins / total_matches * 100) if total_matches > 0 else 0

        # Рейтинг
        try:
            rating = Rating.objects.get(user=user)
            context["rating"] = rating
        except Rating.DoesNotExist:
            context["rating"] = None

        # Последние матчи (10)
        recent_matches = (
            matches.filter(status="FINISHED")
            .select_related("tournament", "player1", "player2", "winner")
            .order_by("-updated_at")[:10]
        )

        # Активные турниры
        active_tournaments = Tournament.objects.filter(
            participants__user=user, status__in=["UPCOMING", "ONGOING"]
        ).distinct()

        # Завершенные турниры
        completed_tournaments = Tournament.objects.filter(
            participants__user=user, status="FINISHED"
        ).distinct()

        # История рейтинга (последние 30 записей)
        rating_history = RatingHistory.objects.filter(user=user).order_by(
            "-created_at"
        )[:30]

        # Достижения
        tournament_wins = matches.filter(
            winner=user, tournament__status="FINISHED", round__in=["Финал", "Final"]
        ).count()

        tournament_finals = matches.filter(
            Q(player1=user) | Q(player2=user),
            tournament__status="FINISHED",
            round__in=["Финал", "Final"],
        ).count()

        tournament_semifinals = matches.filter(
            Q(player1=user) | Q(player2=user),
            tournament__status="FINISHED",
            round__in=["Полуфинал", "Semi-Final", "1/2 финала"],
        ).count()

        # Серия побед/поражений
        recent_results = []
        for match in matches.filter(status="FINISHED").order_by("-updated_at")[:10]:
            if match.winner == user:
                recent_results.append("W")
            else:
                recent_results.append("L")

        # Текущая серия
        current_streak = 0
        streak_type = None
        for result in recent_results:
            if streak_type is None:
                streak_type = result
                current_streak = 1
            elif result == streak_type:
                current_streak += 1
            else:
                break

        context.update(
            {
                "tournaments_count": tournaments_count,
                "wins": wins,
                "losses": losses,
                "total_matches": total_matches,
                "win_percentage": round(win_percentage, 1),
                "recent_matches": recent_matches,
                "active_tournaments": active_tournaments,
                "completed_tournaments": completed_tournaments,
                "is_viewing_own_profile": (self.request.user == user),
                "rating_history": rating_history,
                "tournament_wins": tournament_wins,
                "tournament_finals": tournament_finals,
                "tournament_semifinals": tournament_semifinals,
                "recent_results": "".join(recent_results),
                "current_streak": current_streak,
                "streak_type": "побед" if streak_type == "W" else "поражений",
            }
        )

        return context


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    """View for editing user profile."""

    model = User
    form_class = UserProfileForm
    template_name = "accounts/profile_edit.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy("profile", kwargs={"username": self.request.user.username})
