"""Management command to populate database with sample data."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import random

from tournaments.models import (
    Tournament, Match, Participant, CourtLocation, 
    PartnerSearch, Rating, Referral
)

User = get_user_model()


class Command(BaseCommand):
    help = "Populate database with sample tennis data"

    def handle(self, *args, **options):
        self.stdout.write("Creating sample data...")

        # Создание кортов
        courts = []
        regions = ["NORTH", "SOUTH", "CENTER", "WEST", "EAST"]
        court_names = [
            "Tennis Club Elite", "Moscow Tennis Palace", "Metro Center",
            "Sokolniki Club", "Rublevo-Arkhyz", "Bitsa Park", "Luzhniki",
            "VTB Arena", "Olympic Complex", "City Courts"
        ]
        
        for i, name in enumerate(court_names):
            court = CourtLocation.objects.create(
                name=name,
                address=f"ул. Тестовая, д. {i+1}",
                city="Москва",
                region=random.choice(regions),
                cost_per_hour=random.randint(800, 2500),
                phone=f"+7-999-{random.randint(1000000, 9999999)}",
                working_hours="07:00 - 00:00",
                facilities="Раздевалки, Душ, Парковка, Кафе",
                has_indoor=random.choice([True, False]),
                has_outdoor=True,
                is_active=True
            )
            courts.append(court)
        
        self.stdout.write(f"✓ Created {len(courts)} courts")

        # Получение существующих пользователей
        users = list(User.objects.all())
        
        if len(users) < 5:
            self.stdout.write("⚠ Need at least 5 users. Skipping some sample data...")
            return

        # Создание рейтингов для пользователей
        ratings = []
        for user in users[:10]:  # Только первые 10 пользователей
            rating, created = Rating.objects.get_or_create(
                user=user,
                defaults={
                    'ntrp_level': random.choice(['1.5', '2.0', '2.5', '3.0', '3.5', '4.0']),
                    'matches_played': random.randint(5, 50),
                    'matches_won': random.randint(0, 30),
                    'tournament_wins': random.randint(0, 3),
                    'points': random.randint(1000, 3000),
                }
            )
            if created:
                ratings.append(rating)

        # Обновление рейтинговых позиций
        sorted_ratings = sorted(Rating.objects.all(), key=lambda r: r.points, reverse=True)
        for idx, rating in enumerate(sorted_ratings, start=1):
            rating.rank_position = idx
            rating.save(update_fields=['rank_position'])

        self.stdout.write(f"✓ Created ratings for {len(ratings)} players")

        # Создание поисков партнеров
        partner_searches = []
        sports = ['TENNIS', 'TABLE_TENNIS', 'BADMINTON', 'BEACH_TENNIS']
        levels = ['1.5', '2.0', '2.5', '3.0', '3.5', '4.0', '4.5']
        times = ['Будни вечером', 'Выходные днем', 'Выходные вечером', 'Любое время']
        
        for user in users[:8]:
            if random.random() > 0.4:  # 60% пользователей имеют заявки
                ps = PartnerSearch.objects.create(
                    user=user,
                    sport_type=random.choice(sports),
                    skill_level=random.choice(levels),
                    preferred_time=random.choice(times),
                    preferred_location=random.choice(regions),
                    contact_info=user.phone or f"+7-999-{random.randint(1000000, 9999999)}",
                    is_active=True
                )
                partner_searches.append(ps)
        
        self.stdout.write(f"✓ Created {len(partner_searches)} partner searches")

        # Создание реферальных ссылок (для существующих турниров)
        referrals = []
        tournaments = list(Tournament.objects.all()[:3])
        
        if tournaments and len(users) >= 2:
            for tournament in tournaments:
                for _ in range(2):
                    try:
                        referrer = random.choice(users[:5])
                        referred = random.choice([u for u in users if u != referrer])
                        
                        referral = Referral.objects.create(
                            referrer=referrer,
                            referred=referred,
                            tournament=tournament,
                            bonus_amount=500,
                            status=random.choice(['PENDING', 'PAID'])
                        )
                        referrals.append(referral)
                    except:
                        pass
        
        self.stdout.write(f"✓ Created {len(referrals)} referrals")

        self.stdout.write(self.style.SUCCESS("✓ All sample data created successfully!"))
