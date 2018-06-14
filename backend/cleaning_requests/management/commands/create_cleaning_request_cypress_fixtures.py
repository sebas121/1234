from django.core.management.base import BaseCommand

from decimal import Decimal
from mixer.backend.django import mixer


class Command(BaseCommand):
    help = ('Creates test data for Cleaning Request Cypress test run.')

    def setup_superuser(self):
        """
        Creates an admin user in case we want to login to the Django admin.

        """
        self.admin = self.create_user(
            email="admin@example.com",
            username="admin",
            is_superuser=True,
            is_staff=True)

    def create_user(self, password='test123', **kwargs):
        user = mixer.blend('auth.User', **kwargs)
        user.set_password(password)
        user.save()
        return user

    def setup_pricing_models(self):
        """Creates pricing models for the site."""
        city1 = mixer.blend(
            'pricing.City',
            name='Singapore',
            slug='singapore',
            gst=Decimal('1.5'),
            currency_code='SGD')
        city2 = mixer.blend(
            'pricing.City',
            name='Yangon',
            slug='yangon',
            gst=Decimal('1.5'),
            currency_code='MMK')
        mixer.blend(
            'pricing.CleaningExtra', name='Ironing', slug='ironing', hours=2)
        mixer.blend(
            'pricing.CleaningExtra',
            name='Laundry wash & dry',
            slug='laundry-wash-dry',
            hours=5)
        mixer.blend('pricing.CleaningHour')
        mixer.blend(
            'pricing.CleaningPrice',
            city=city1,
            number_of_months=3,
            sessions_per_week=1,
            hourly_rate=Decimal('2.00'))
        mixer.blend(
            'pricing.CleaningPrice',
            city=city2,
            number_of_months=3,
            sessions_per_week=1,
            hourly_rate=Decimal('23.00'))

    def handle(self, *args, **options):
        self.setup_superuser()
        self.setup_pricing_models()
