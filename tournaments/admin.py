"""Admin configuration for tournaments app."""

from django.contrib import admin
from .models import (
    Tournament,
    Participant,
    Match,
    CourtLocation,
    PartnerSearch,
    Rating,
    Referral,
    RatingHistory,
)


class ParticipantInline(admin.TabularInline):
    """Inline admin for participants."""

    model = Participant
    extra = 0
    fields = ["user", "seed", "registered_at"]
    readonly_fields = ["registered_at"]


class MatchInline(admin.TabularInline):
    """Inline admin for matches."""

    model = Match
    extra = 0
    fields = ["round", "player1", "player2", "status", "winner"]
    readonly_fields = ["created_at"]


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    """Admin interface for Tournament model."""

    list_display = [
        "name",
        "category",
        "level",
        "region",
        "tournament_type",
        "start_date",
        "status_detail",
        "participants_count",
        "entry_fee",
    ]
    list_filter = [
        "category",
        "level",
        "region",
        "status",
        "status_detail",
        "tournament_type",
        "start_date",
    ]
    search_fields = ["name", "description", "location"]
    date_hierarchy = "start_date"
    ordering = ["-start_date"]
    inlines = [ParticipantInline, MatchInline]
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("name", "category", "level", "description")},
        ),
        ("Даты и место", {"fields": ("start_date", "end_date", "location", "region")}),
        ("Статус", {"fields": ("status", "status_detail")}),
        (
            "Параметры турнира",
            {
                "fields": (
                    "tournament_type",
                    "scoring_system",
                    "max_participants",
                    "max_rounds",
                )
            },
        ),
        ("Финансы и призы", {"fields": ("entry_fee", "prize_description")}),
        ("Дополнительно", {"fields": ("image",)}),
    )

    def participants_count(self, obj):
        """Get current participants count."""
        return f"{obj.participants.count()}/{obj.max_participants}"

    participants_count.short_description = "Участники"


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    """Admin interface for Participant model."""

    list_display = ["user", "tournament", "seed", "registered_at"]
    list_filter = ["tournament", "registered_at"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "tournament__name",
    ]
    ordering = ["tournament", "seed"]
    date_hierarchy = "registered_at"


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """Admin interface for Match model."""

    list_display = [
        "tournament",
        "round",
        "player1",
        "player2",
        "scheduled_date",
        "status",
        "score_status",
        "winner",
    ]
    list_filter = [
        "tournament",
        "status",
        "scheduled_date",
        "score_confirmed_by_player1",
        "score_confirmed_by_player2",
    ]
    search_fields = ["player1__username", "player2__username", "tournament__name"]
    date_hierarchy = "scheduled_date"
    ordering = ["-scheduled_date"]
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("tournament", "round", "player1", "player2")},
        ),
        (
            "Планирование",
            {"fields": ("scheduled_date", "deadline", "court_location", "location")},
        ),
        (
            "Детали игры",
            {
                "fields": (
                    "court_cost",
                    "balls_confirmed",
                    "contact_initiated_by",
                    "actual_date",
                )
            },
        ),
        (
            "Результаты",
            {
                "fields": (
                    ("player1_set1", "player2_set1"),
                    ("player1_set2", "player2_set2"),
                    ("player1_set3", "player2_set3"),
                    "score_confirmed_by_player1",
                    "score_confirmed_by_player2",
                    "winner",
                    "status",
                )
            },
        ),
    )

    def score_status(self, obj):
        """Get score confirmation status."""
        if obj.is_score_confirmed():
            return "✓ Подтвержден"
        elif obj.score_confirmed_by_player1 or obj.score_confirmed_by_player2:
            return "⚠ Частично"
        return "✗ Не подтвержден"

    score_status.short_description = "Статус счета"


@admin.register(CourtLocation)
class CourtLocationAdmin(admin.ModelAdmin):
    """Admin interface for CourtLocation model."""

    list_display = [
        "name",
        "city",
        "region",
        "cost_per_hour",
        "court_types",
        "is_active",
    ]
    list_filter = ["city", "region", "is_active", "has_indoor", "has_outdoor"]
    search_fields = ["name", "address", "phone"]
    ordering = ["city", "region", "name"]
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("name", "address", "city", "region", "phone")},
        ),
        (
            "Параметры",
            {"fields": ("cost_per_hour", "working_hours", "has_indoor", "has_outdoor")},
        ),
        ("Удобства", {"fields": ("facilities",)}),
        ("Статус", {"fields": ("is_active",)}),
    )

    def court_types(self, obj):
        """Get court types."""
        types = []
        if obj.has_indoor:
            types.append("Крытый")
        if obj.has_outdoor:
            types.append("Открытый")
        return ", ".join(types) if types else "-"

    court_types.short_description = "Тип корта"


@admin.register(PartnerSearch)
class PartnerSearchAdmin(admin.ModelAdmin):
    """Admin interface for PartnerSearch model."""

    list_display = [
        "user",
        "sport_type",
        "skill_level",
        "preferred_location",
        "is_active",
        "created_at",
    ]
    list_filter = ["sport_type", "skill_level", "is_active", "created_at"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "preferred_location",
    ]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    fieldsets = (
        ("Пользователь", {"fields": ("user",)}),
        (
            "Параметры поиска",
            {
                "fields": (
                    "sport_type",
                    "skill_level",
                    "preferred_time",
                    "preferred_location",
                )
            },
        ),
        ("Контакты", {"fields": ("contact_info",)}),
        ("Статус", {"fields": ("is_active",)}),
    )


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Admin interface for Rating model."""

    list_display = [
        "user",
        "ntrp_level",
        "points",
        "rank_position",
        "matches_played",
        "matches_won",
        "win_rate",
        "tournament_wins",
    ]
    list_filter = ["ntrp_level"]
    search_fields = ["user__username", "user__first_name", "user__last_name"]
    ordering = ["-points", "rank_position"]
    readonly_fields = ["updated_at"]
    fieldsets = (
        ("Игрок", {"fields": ("user", "ntrp_level")}),
        ("Рейтинг", {"fields": ("points", "rank_position")}),
        (
            "Статистика",
            {"fields": ("matches_played", "matches_won", "tournament_wins")},
        ),
        ("Обновление", {"fields": ("updated_at",)}),
    )

    def win_rate(self, obj):
        """Get win percentage."""
        return f"{obj.win_percentage()}%"

    win_rate.short_description = "% побед"


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    """Admin interface for Referral model."""

    list_display = [
        "referrer",
        "referred",
        "tournament",
        "bonus_amount",
        "status",
        "created_at",
        "paid_at",
    ]
    list_filter = ["status", "created_at", "paid_at"]
    search_fields = [
        "referrer__username",
        "referred__username",
        "tournament__name",
    ]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at"]
    fieldsets = (
        ("Участники", {"fields": ("referrer", "referred", "tournament")}),
        ("Бонус", {"fields": ("bonus_amount", "status")}),
        ("Даты", {"fields": ("created_at", "paid_at")}),
    )

    fieldsets = [
        (
            "Основная информация",
            {
                "fields": (
                    "tournament",
                    "round",
                    "player1",
                    "player2",
                    "scheduled_date",
                    "location",
                    "status",
                )
            },
        ),
        (
            "Результаты",
            {
                "fields": (
                    "player1_set1",
                    "player2_set1",
                    "player1_set2",
                    "player2_set2",
                    "player1_set3",
                    "player2_set3",
                    "winner",
                )
            },
        ),
    ]


@admin.register(RatingHistory)
class RatingHistoryAdmin(admin.ModelAdmin):
    """Admin interface for RatingHistory model."""

    list_display = ["user", "points", "change", "tournament", "match", "created_at"]
    list_filter = ["created_at", "tournament"]
    search_fields = ["user__username", "user__first_name", "user__last_name", "reason"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at"]
    fieldsets = (
        (
            "Игрок",
            {"fields": ("user", "points", "change")},
        ),
        (
            "Связи",
            {"fields": ("match", "tournament", "reason")},
        ),
        (
            "Дата",
            {"fields": ("created_at",)},
        ),
    )
