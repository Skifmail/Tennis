"""Management command to create sample data."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from tournaments.models import Tournament, Match, Participant
from news.models import Article


class Command(BaseCommand):
    """Create sample data for testing."""

    help = "Создает тестовые данные для проекта"

    def handle(self, *args, **options):
        self.stdout.write("Создание тестовых данных...")

        # Создаем пользователей
        users = []
        names = [
            ("Иван", "Петров"), ("Мария", "Соколова"), ("Петр", "Иванов"),
            ("Елена", "Смирнова"), ("Алексей", "Федоров"), ("Анна", "Морозова"),
            ("Дмитрий", "Волков"), ("Ольга", "Сизова"), ("Сергей", "Новиков"),
            ("Светлана", "Васильева"), ("Владимир", "Кузнецов"), ("Екатерина", "Благова"),
            ("Николай", "Орлов"), ("Вера", "Парфенова"), ("Павел", "Казаков"),
        ]
        
        for i, (first_name, last_name) in enumerate(names, start=1):
            user, created = User.objects.get_or_create(
                username=f"player{i}",
                defaults={
                    "email": f"player{i}@tennis.local",
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone": f"+7-{900 + i}-{100 + i*10}-{50 + i*2}-{10 + i}",
                    "rating": 1000 + (i * 50),
                    "gender": "M" if i % 2 == 0 else "F",
                    "city": "Москва" if i % 3 == 0 else "Санкт-Петербург" if i % 3 == 1 else "Казань",
                },
            )
            if created:
                user.set_password("password123")
                user.save()
                users.append(user)
                self.stdout.write(f"✓ Создан пользователь: {user.username} ({user.get_full_name()})")

        # Создаем турниры
        tournaments_data = [
            {
                "name": "Весенний турнир 2026",
                "category": "MEN",
                "status": "UPCOMING",
                "description": "Мужской турнир для начинающих игроков",
            },
            {
                "name": "Женский чемпионат",
                "category": "WOMEN",
                "status": "ONGOING",
                "description": "Женский турнир высокого уровня",
            },
            {
                "name": "Летний кубок",
                "category": "MIXED",
                "status": "UPCOMING",
                "description": "Смешанный турнир для всех уровней",
            },
        ]

        for i, tour_data in enumerate(tournaments_data):
            tournament, created = Tournament.objects.get_or_create(
                name=tour_data["name"],
                defaults={
                    "category": tour_data["category"],
                    "status": tour_data["status"],
                    "description": tour_data["description"],
                    "start_date": timezone.now().date() + timedelta(days=7 + i * 14),
                    "end_date": timezone.now().date() + timedelta(days=14 + i * 14),
                    "location": "Теннисный центр, Рига",
                    "max_participants": 16,
                },
            )
            if created:
                self.stdout.write(f"Создан турнир: {tournament.name}")

                # Добавляем участников
                for j, user in enumerate(users[:8]):
                    Participant.objects.get_or_create(
                        tournament=tournament, user=user, defaults={"seed": j + 1}
                    )

        # Создаем новости
        articles_data = [
            {
                "title": "Открытие нового теннисного сезона",
                "slug": "otkrytie-novogo-sezona",
                "content": "Начался новый теннисный сезон! Приглашаем всех любителей тенниса принять участие в турнирах.",
            },
            {
                "title": "Результаты зимнего турнира",
                "slug": "rezultaty-zimnego-turnira",
                "content": "Зимний турнир завершился победой игрока №5. Поздравляем победителя!",
            },
            {
                "title": "Новые правила участия",
                "slug": "novye-pravila",
                "content": "Обратите внимание на обновленные правила участия в турнирах.",
            },
        ]

        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = User.objects.first()

        for article_data in articles_data:
            article, created = Article.objects.get_or_create(
                slug=article_data["slug"],
                defaults={
                    "title": article_data["title"],
                    "content": article_data["content"],
                    "author": admin_user,
                    "published": True,
                },
            )
            if created:
                self.stdout.write(f"Создана статья: {article.title}")

        self.stdout.write(
            self.style.SUCCESS("✓ Тестовые данные успешно созданы!")
        )
        self.stdout.write(
            f"Создано пользователей: {len(users)}, турниров: {len(tournaments_data)}, статей: {len(articles_data)}"
        )
