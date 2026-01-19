"""Models for tournaments app."""

from django.db import models
from django.conf import settings


class Tournament(models.Model):
    """Tournament model."""

    CATEGORY_CHOICES = [
        ("MEN", "Мужская"),
        ("WOMEN", "Женская"),
        ("MIXED", "Смешанные"),
    ]

    STATUS_CHOICES = [
        ("UPCOMING", "Предстоящий"),
        ("ONGOING", "Идёт"),
        ("FINISHED", "Завершён"),
    ]

    LEVEL_CHOICES = [
        ("1.5-2.5", "3я категория (1.5-2.5)"),
        ("2.5-3.5", "2я категория (2.5-3.5)"),
        ("3.5-4.5", "1я категория (3.5-4.5)"),
        ("4.5-5.5", "Мастерс (4.5-5.5)"),
        ("5.5-6.5", "Профи (5.5-6.5)"),
    ]

    REGION_CHOICES = [
        ("NORTH", "Север"),
        ("SOUTH", "Юг"),
        ("CENTER", "Центр"),
        ("ALL", "Вся Москва"),
    ]

    TYPE_CHOICES = [
        ("MULTI_DAY", "Многодневный"),
        ("WEEKEND", "Выходного дня"),
    ]

    SCORING_CHOICES = [
        ("OLYMPIC", "Олимпийская система"),
        ("ROUND_ROBIN", "Круговая система"),
    ]

    STATUS_DETAIL_CHOICES = [
        ("ACCEPTING", "Прием заявок"),
        ("IN_PROGRESS", "Идут игры"),
        ("COMPLETED", "Завершен"),
    ]

    name = models.CharField("Название", max_length=200)
    category = models.CharField("Категория", max_length=10, choices=CATEGORY_CHOICES)
    level = models.CharField(
        "Уровень игры", max_length=10, choices=LEVEL_CHOICES, default="2.5-3.5"
    )
    description = models.TextField("Описание", blank=True)
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")
    status = models.CharField(
        "Статус", max_length=10, choices=STATUS_CHOICES, default="UPCOMING"
    )
    status_detail = models.CharField(
        "Детальный статус",
        max_length=15,
        choices=STATUS_DETAIL_CHOICES,
        default="ACCEPTING",
    )
    location = models.CharField("Место проведения", max_length=200, blank=True)
    region = models.CharField(
        "Регион", max_length=10, choices=REGION_CHOICES, default="ALL"
    )
    max_participants = models.IntegerField("Максимум участников", default=8)
    entry_fee = models.DecimalField(
        "Взнос за участие", max_digits=10, decimal_places=2, default=800
    )
    max_rounds = models.IntegerField(
        "Количество игр",
        default=3,
        help_text="Каждый игрок играет указанное количество матчей",
    )
    tournament_type = models.CharField(
        "Тип турнира", max_length=15, choices=TYPE_CHOICES, default="MULTI_DAY"
    )
    scoring_system = models.CharField(
        "Система проведения", max_length=15, choices=SCORING_CHOICES, default="OLYMPIC"
    )
    prize_description = models.TextField(
        "Описание приза",
        blank=True,
        default="Победитель получает бесплатное участие в следующем турнире",
    )
    image = models.ImageField(
        "Изображение", upload_to="tournaments/", null=True, blank=True
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Турнир"
        verbose_name_plural = "Турниры"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Participant(models.Model):
    """Tournament participant model."""

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="participants",
        verbose_name="Турнир",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="participations",
        verbose_name="Участник",
    )
    seed = models.IntegerField("Номер посева", null=True, blank=True)
    registered_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"
        unique_together = ["tournament", "user"]
        ordering = ["seed", "registered_at"]

    def __str__(self):
        return f"{self.user.username} - {self.tournament.name}"


class Match(models.Model):
    """Match model."""

    STATUS_CHOICES = [
        ("SCHEDULED", "Запланирован"),
        ("IN_PROGRESS", "Идёт"),
        ("FINISHED", "Завершён"),
        ("CANCELLED", "Отменён"),
    ]

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="matches",
        verbose_name="Турнир",
    )
    round = models.CharField("Раунд", max_length=50)
    player1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_as_player1",
        verbose_name="Игрок 1",
    )
    player2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_as_player2",
        verbose_name="Игрок 2",
    )
    court_location = models.ForeignKey(
        "CourtLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches",
        verbose_name="Корт",
    )
    scheduled_date = models.DateTimeField("Дата и время", null=True, blank=True)
    deadline = models.DateTimeField(
        "Дедлайн на игру",
        null=True,
        blank=True,
        help_text="Время на каждую игру - 1 неделя",
    )
    actual_date = models.DateTimeField("Фактическая дата игры", null=True, blank=True)
    location = models.CharField("Место", max_length=200, blank=True)
    status = models.CharField(
        "Статус", max_length=15, choices=STATUS_CHOICES, default="SCHEDULED"
    )
    court_cost = models.DecimalField(
        "Стоимость корта", max_digits=10, decimal_places=2, null=True, blank=True
    )
    balls_confirmed = models.BooleanField(
        "Мячи согласованы", default=False, help_text="Не менее 3 новых мячей"
    )
    contact_initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initiated_contacts",
        verbose_name="Инициатор контакта",
        help_text="Принимающая сторона",
    )
    player1_set1 = models.IntegerField("Сет 1 (Игрок 1)", null=True, blank=True)
    player1_set2 = models.IntegerField("Сет 2 (Игрок 1)", null=True, blank=True)
    player1_set3 = models.IntegerField("Сет 3 (Игрок 1)", null=True, blank=True)
    player2_set1 = models.IntegerField("Сет 1 (Игрок 2)", null=True, blank=True)
    player2_set2 = models.IntegerField("Сет 2 (Игрок 2)", null=True, blank=True)
    player2_set3 = models.IntegerField("Сет 3 (Игрок 2)", null=True, blank=True)
    score_confirmed_by_player1 = models.BooleanField(
        "Счет подтвержден игроком 1", default=False
    )
    score_confirmed_by_player2 = models.BooleanField(
        "Счет подтвержден игроком 2", default=False
    )
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_matches",
        verbose_name="Победитель",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"
        ordering = ["scheduled_date", "round"]

    def __str__(self):
        return f"{self.player1.username} vs {self.player2.username}"

    def get_score(self):
        """Return match score as string."""
        if not self.player1_set1:
            return "Счёт не указан"

        sets = []
        for i in range(1, 4):
            p1_score = getattr(self, f"player1_set{i}")
            p2_score = getattr(self, f"player2_set{i}")
            if p1_score is not None and p2_score is not None:
                sets.append(f"{p1_score}:{p2_score}")

        return " ".join(sets)

    def is_score_confirmed(self):
        """Check if both players confirmed the score."""
        return self.score_confirmed_by_player1 and self.score_confirmed_by_player2


class CourtLocation(models.Model):
    """Tennis court location model."""

    REGION_CHOICES = [
        ("NORTH", "Север"),
        ("SOUTH", "Юг"),
        ("CENTER", "Центр"),
        ("WEST", "Запад"),
        ("EAST", "Восток"),
    ]

    name = models.CharField("Название", max_length=200)
    address = models.CharField("Адрес", max_length=300)
    city = models.CharField("Город", max_length=100, default="Москва")
    region = models.CharField("Регион", max_length=10, choices=REGION_CHOICES)
    cost_per_hour = models.DecimalField(
        "Стоимость часа", max_digits=10, decimal_places=2
    )
    phone = models.CharField("Телефон", max_length=50, blank=True)
    working_hours = models.CharField(
        "Часы работы", max_length=100, default="07:00 - 00:00"
    )
    facilities = models.TextField(
        "Удобства", blank=True, help_text="Раздевалки, душ, парковка и т.д."
    )
    has_indoor = models.BooleanField("Крытый корт", default=False)
    has_outdoor = models.BooleanField("Открытый корт", default=True)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Корт"
        verbose_name_plural = "Корты"
        ordering = ["city", "region", "name"]

    def __str__(self):
        return f"{self.name} ({self.region}) - {self.cost_per_hour} ₽/час"


class PartnerSearch(models.Model):
    """Partner search model for finding tennis partners."""

    SPORT_CHOICES = [
        ("TENNIS", "Теннис"),
        ("TABLE_TENNIS", "Настольный теннис"),
        ("BADMINTON", "Бадминтон"),
        ("BEACH_TENNIS", "Пляжный теннис"),
        ("PADEL", "Падл-теннис"),
        ("SQUASH", "Сквош"),
        ("PICKLEBALL", "Пиклбол"),
    ]

    LEVEL_CHOICES = [
        ("1.0", "1.0 - Начинающий"),
        ("1.5", "1.5"),
        ("2.0", "2.0"),
        ("2.5", "2.5"),
        ("3.0", "3.0 - Средний"),
        ("3.5", "3.5"),
        ("4.0", "4.0"),
        ("4.5", "4.5 - Продвинутый"),
        ("5.0", "5.0"),
        ("5.5", "5.5"),
        ("6.0", "6.0 - Профессионал"),
        ("6.5", "6.5"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="partner_searches",
        verbose_name="Пользователь",
    )
    sport_type = models.CharField(
        "Вид спорта", max_length=20, choices=SPORT_CHOICES, default="TENNIS"
    )
    skill_level = models.CharField(
        "Уровень игры (NTRP)", max_length=5, choices=LEVEL_CHOICES
    )
    preferred_time = models.CharField(
        "Предпочитаемое время",
        max_length=200,
        help_text="Например: будни вечером, выходные днем",
    )
    preferred_location = models.CharField(
        "Предпочитаемое место", max_length=200, help_text="Район или название корта"
    )
    contact_info = models.TextField("Контактная информация", blank=True)
    is_active = models.BooleanField("Активная заявка", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Поиск партнера"
        verbose_name_plural = "Поиск партнеров"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.get_sport_type_display()} ({self.skill_level})"


class Rating(models.Model):
    """Player rating model."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="player_rating",
        verbose_name="Игрок",
    )
    ntrp_level = models.CharField("Уровень NTRP", max_length=5, default="3.0")
    matches_played = models.IntegerField("Матчей сыграно", default=0)
    matches_won = models.IntegerField("Матчей выиграно", default=0)
    tournament_wins = models.IntegerField("Побед в турнирах", default=0)
    points = models.IntegerField("Рейтинговые очки", default=1000)
    rank_position = models.IntegerField("Позиция в рейтинге", null=True, blank=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"
        ordering = ["-points", "rank_position"]

    def __str__(self):
        return f"{self.user.username} - {self.points} очков (NTRP {self.ntrp_level})"

    def win_percentage(self):
        """Calculate win percentage."""
        if self.matches_played == 0:
            return 0
        return round((self.matches_won / self.matches_played) * 100, 1)


class Referral(models.Model):
    """Referral system model."""

    STATUS_CHOICES = [
        ("PENDING", "Ожидает"),
        ("PAID", "Выплачено"),
        ("CANCELLED", "Отменено"),
    ]

    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referrals_made",
        verbose_name="Пригласивший",
    )
    referred = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referred_by",
        verbose_name="Приглашенный",
    )
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="referrals",
        verbose_name="Турнир",
    )
    bonus_amount = models.DecimalField(
        "Сумма бонуса", max_digits=10, decimal_places=2, default=500
    )
    status = models.CharField(
        "Статус", max_length=10, choices=STATUS_CHOICES, default="PENDING"
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    paid_at = models.DateTimeField("Дата выплаты", null=True, blank=True)

    class Meta:
        verbose_name = "Реферал"
        verbose_name_plural = "Рефералы"
        ordering = ["-created_at"]
        unique_together = ["referrer", "referred", "tournament"]

    def __str__(self):
        return f"{self.referrer.username} -> {self.referred.username} ({self.tournament.name})"


class RatingHistory(models.Model):
    """Model for tracking rating changes over time."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rating_history",
        verbose_name="Игрок",
    )
    points = models.IntegerField("Рейтинговые очки")
    match = models.ForeignKey(
        Match,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rating_changes",
        verbose_name="Матч",
    )
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rating_changes",
        verbose_name="Турнир",
    )
    change = models.IntegerField(
        "Изменение",
        default=0,
        help_text="Положительное значение - рост, отрицательное - падение",
    )
    reason = models.CharField("Причина", max_length=200, blank=True)
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "История рейтинга"
        verbose_name_plural = "История рейтингов"
        ordering = ["-created_at"]

    def __str__(self):
        change_str = f"+{self.change}" if self.change > 0 else str(self.change)
        return f"{self.user.username} - {self.points} ({change_str})"
