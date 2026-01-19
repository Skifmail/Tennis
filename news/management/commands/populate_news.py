"""Management command to populate sample news articles."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from news.models import Article

User = get_user_model()


class Command(BaseCommand):
    """Create sample news articles."""

    help = "Populate database with sample news articles"

    def handle(self, *args, **options):
        """Create sample articles."""
        # Get admin user
        try:
            admin = User.objects.get(username="admin")
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("Admin user not found. Please create admin user first.")
            )
            return

        # Sample articles
        articles_data = [
            {
                "title": "Весенний турнир 2026 начался!",
                "slug": "spring-tournament-2026-started",
                "content": """
                <h3>Стартовал долгожданный Весенний турнир 2026!</h3>
                <p>Более 50 участников собрались на площадках города для участия в самом большом 
                теннисном событии сезона. Турнир проводится в двух категориях: любительский и профессиональный уровень.</p>
                <h4>Главные события:</h4>
                <ul>
                    <li>Регистрация завершена, начинаются матчи первого раунда</li>
                    <li>Трансляция матчей финального дня</li>
                    <li>Прямые эфиры в нашем мобильном приложении</li>
                </ul>
                <p>Следите за обновлениями!</p>
                """,
            },
            {
                "title": "Топ 10 игроков месяца",
                "slug": "top-10-players-month",
                "content": """
                <h3>Лучшие игроки месяца</h3>
                <p>По итогам всех турниров этого месяца мы составили рейтинг лучших игроков:</p>
                <ol>
                    <li>Иван Петров - 2500 очков</li>
                    <li>Мария Сидорова - 2400 очков</li>
                    <li>Сергей Иванов - 2300 очков</li>
                    <li>Анна Смирнова - 2250 очков</li>
                    <li>Алексей Волков - 2200 очков</li>
                </ol>
                <p>Поздравляем всех победителей!</p>
                """,
            },
            {
                "title": "Новая функция: Поиск партнера",
                "slug": "new-feature-partner-search",
                "content": """
                <h3>Новая функция на платформе!</h3>
                <p>Теперь вы можете искать партнеров для игры прямо в приложении!</p>
                <h4>Что это дает:</h4>
                <ul>
                    <li>Быстрый поиск партнеров нужного уровня</li>
                    <li>Фильтрация по городу и виду спорта</li>
                    <li>Прямая связь с другими игроками</li>
                </ul>
                <p>Переходите в раздел "Поиск партнера" и начните искать!</p>
                """,
            },
            {
                "title": "Обновление системы рейтингов",
                "slug": "rating-system-update",
                "content": """
                <h3>Улучшена система расчета рейтинга</h3>
                <p>Мы обновили алгоритм расчета рейтинга для более справедливой оценки мастерства игроков.</p>
                <h4>Изменения:</h4>
                <ul>
                    <li>Новая система расчета очков</li>
                    <li>Учет уровня оппонента</li>
                    <li>Более частые обновления рейтинга</li>
                </ul>
                <p>Система станет еще более справедливой!</p>
                """,
            },
            {
                "title": "Советы для улучшения игры",
                "slug": "tips-to-improve-game",
                "content": """
                <h3>5 советов для улучшения вашей игры в теннис</h3>
                <p>Хотите улучшить свой результат? Вот несколько проверенных советов:</p>
                <ol>
                    <li><strong>Тренируйтесь регулярно</strong> - минимум 3 раза в неделю</li>
                    <li><strong>Работайте над техникой</strong> - обратитесь к тренеру</li>
                    <li><strong>Играйте с более сильными оппонентами</strong> - это развивает мастерство</li>
                    <li><strong>Следите за физической формой</strong> - гибкость и выносливость важны</li>
                    <li><strong>Анализируйте свои матчи</strong> - учитесь на ошибках</li>
                </ol>
                <p>Удачи в тренировках!</p>
                """,
            },
        ]

        # Create articles
        for data in articles_data:
            article, created = Article.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "content": data["content"],
                    "author": admin,
                    "published": True,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created article: {article.title}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠ Article already exists: {article.title}")
                )

        self.stdout.write(
            self.style.SUCCESS("\n✅ Sample articles populated successfully!")
        )
