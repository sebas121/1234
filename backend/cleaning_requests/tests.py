from decimal import Decimal

from django.utils import timezone
from django.test import TestCase

from pricing.models import City, CleaningHour

from . import forms


class CleaningRequest_Form_Test(TestCase):
    def setUp(self):
        City.objects.create(
            name="Nevada",
            slug="nevada",
            gst=Decimal('0.1'))
        City.objects.create(
            name="Genosha",
            slug="genosha",
            gst=Decimal('1'))
        CleaningHour.objects.create()

    def test_CleaningRequestForm_valid(self):
        form = forms.CleaningRequestForm(
            data={
                    'city': 1,
                    'name': "Ben",
                    'zip': 777,
                    'schedule': 1,
                    'months': 3,
                    'num_bedrooms': 2,
                    'num_bathrooms': 1,
                    'num_hours': Decimal('12'),
                    'first_visit': timezone.now(),
                    'user_email': 'ben@polecats.com',
                    'user_address': 'On the road...'
                 }
        )
        self.assertTrue(form.is_valid())

    def test_CleaningRequestForm_invalid(self):
        # Missing city
        form = forms.CleaningRequestForm(
            data={
                    'name': "Ben",
                    'zip': 777,
                    'schedule': 1,
                    'months': 3,
                    'num_bedrooms': 2,
                    'num_bathrooms': 1,
                    'first_visit': timezone.now(),
                    'user_email': 'ben@polecats.com',
                    'user_address': 'On the road...'
                 }
        )
        self.assertEqual(form.errors['city'], ['This field is required.'])

        # Missing name
        form = forms.CleaningRequestForm(
            data={
                    'city': 1,
                    'zip': 777,
                    'schedule': 1,
                    'months': 3,
                    'num_bedrooms': 2,
                    'num_bathrooms': 1,
                    'first_visit': timezone.now(),
                    'user_email': 'ben@polecats.com',
                    'user_address': 'On the road...'
                 }
        )
        self.assertEqual(form.errors['name'], ['This field is required.'])

        # Missing zip
        form = forms.CleaningRequestForm(
            data={
                    'city': 1,
                    'name': "Ben",
                    'schedule': 1,
                    'months': 3,
                    'num_bedrooms': 2,
                    'num_bathrooms': 1,
                    'first_visit': timezone.now(),
                    'user_email': 'ben@polecats.com',
                    'user_address': 'On the road...'
                 }
        )
        self.assertEqual(form.errors['zip'], ['This field is required.'])

        # Missing schedule
        form = forms.CleaningRequestForm(
            data={
                    'city': 1,
                    'name': "Ben",
                    'zip': 777,
                    'months': 3,
                    'num_bedrooms': 2,
                    'num_bathrooms': 1,
                    'first_visit': timezone.now(),
                    'user_email': 'ben@polecats.com',
                    'user_address': 'On the road...'
                 }
        )
        self.assertEqual(form.errors['schedule'], ['This field is required.'])

        # Missing months
        form = forms.CleaningRequestForm(
            data={
                    'city': 1,
                    'name': "Ben",
                    'zip': 777,
                    'schedule': 1,
                    'num_bedrooms': 2,
                    'num_bathrooms': 1,
                    'first_visit': timezone.now(),
                    'user_email': 'ben@polecats.com',
                    'user_address': 'On the road...'
                 }
        )
        self.assertEqual(form.errors['months'], ['This field is required.'])

        # Missing beds
        form = forms.CleaningRequestForm(
            data={
                    'city': 1,
                    'name': "Ben",
                    'zip': 777,
                    'schedule': 1,
                    'months': 3,
                    'num_bathrooms': 1,
                    'first_visit': timezone.now(),
                    'user_email': 'ben@polecats.com',
                    'user_address': 'On the road...'
                 }
        )
        self.assertEqual(
            form.errors['num_bedrooms'], ['This field is required.'])

        # Missing baths
        form = forms.CleaningRequestForm(
            data={
                    'city': 1,
                    'name': "Ben",
                    'zip': 777,
                    'schedule': 1,
                    'months': 3,
                    'num_bedrooms': 2,
                    'first_visit': timezone.now(),
                    'user_email': 'ben@polecats.com',
                    'user_address': 'On the road...'
                 }
        )
        self.assertEqual(
            form.errors['num_bathrooms'], ['This field is required.'])

        # Missing first_visit
        form = forms.CleaningRequestForm(
            data={
                    'city': 1,
                    'name': "Ben",
                    'zip': 777,
                    'schedule': 1,
                    'months': 3,
                    'num_bedrooms': 4,
                    'num_bathrooms': 2,
                    'user_email': 'ben@polecats.com',
                    'user_address': 'On the road...'
                 }
        )
        self.assertEqual(
            form.errors['first_visit'], ['This field is required.'])

        # Missing email
        form = forms.CleaningRequestForm(
            data={
                    'city': 1,
                    'name': "Ben",
                    'zip': 777,
                    'schedule': 1,
                    'months': 3,
                    'num_bedrooms': 4,
                    'num_bathrooms': 2,
                    'first_visit': timezone.now(),
                    'user_address': 'On the road...'
                 }
        )
        self.assertEqual(
            form.errors['user_email'], ['This field is required.'])

        # Invalid email
        form = forms.CleaningRequestForm(
            data={
                    'city': 1,
                    'name': "Ben",
                    'zip': 777,
                    'schedule': 1,
                    'months': 3,
                    'num_bedrooms': 4,
                    'num_bathrooms': 2,
                    'first_visit': timezone.now(),
                    'user_email': 'ben',
                    'user_address': 'On the road...'
                 }
        )
        self.assertEqual(
            form.errors['user_email'], ['Enter a valid email address.'])

        # Missing user_address
        form = forms.CleaningRequestForm(
            data={
                    'city': 1,
                    'name': "Ben",
                    'zip': 777,
                    'schedule': 1,
                    'months': 3,
                    'num_bedrooms': 4,
                    'num_bathrooms': 2,
                    'first_visit': timezone.now(),
                    'user_email': 'ben@polecats.com',
                 }
        )
        self.assertEqual(
            form.errors['user_address'], ['This field is required.'])

        # Error in hours_override
        form = forms.CleaningRequestForm(
            data={
                    'city': 1,
                    'name': "Ben",
                    'zip': 777,
                    'schedule': 1,
                    'months': 3,
                    'num_bedrooms': 4,
                    'num_bathrooms': 1,
                    'num_hours': Decimal('11'),
                    'first_visit': timezone.now(),
                    'user_email': 'ben@polecats.com',
                    'user_address': 'On the road...'
                 }
        )
        self.assertEqual(
            form.errors['num_hours'],
            ['At least 12.50 hours is required for your request'])
