from django.db import models
from django.db.models import Sum

from decimal import Decimal


class City(models.Model):
    """
    Cities covered by the business.

    :name: Name of the city.
    :slug: Unique identifier for a city. Used in choices / DDLs as the value.
    :gst: Service Tax applicable
    :is_published: Set to false if we are not yet ready to launch our services
      in any of the given cities.
    :currency_code: ISO code of the city's currency.
    """
    name = models.CharField(max_length=128)
    slug = models.SlugField()
    gst = models.DecimalField(max_digits=5, decimal_places=3)
    is_published = models.BooleanField(default=True)
    currency_code = models.CharField(max_length=3)

    def __str__(self):
        return self.name


class CleaningExtra(models.Model):
    """
    The Extra services that customers might want to add to their cleaning
    routine.

    :name: Name of the service.
    :slug: Unique identifier for a service. User in checkboxes as the value.
    :hours: Our hours estimate for the service.
    """

    name = models.CharField(max_length=256)
    slug = models.SlugField()
    hours = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class CleaningHour(models.Model):
    """
    Holds the Minimum Hours, Minimum rooms and extra room increment values.

    :min_hours: Minimum number of hours that will be charged for.
    :min_rooms: Minimum number of rooms that will be charged for.
    :increment: Hours required for each extra room that the user might request.
    """

    min_hours = models.DecimalField(
        default=Decimal('4.0'),
        max_digits=4,
        decimal_places=2,
    )
    min_rooms = models.IntegerField(default=3)
    increment = models.DecimalField(
        default=Decimal('0.5'),
        max_digits=8,
        decimal_places=2,
    )

    def __str__(self):
        return str(self.min_hours)

    def get_work_hours(self, extra_rooms=None, extras=None):
        work_hours = self.min_hours
        if extra_rooms:
            work_hours += extra_rooms * self.increment
        if extras:
            extras_hours = CleaningExtra.objects.filter(
                slug__in=extras).aggregate(Sum('hours'))['hours__sum']
            work_hours += extras_hours
        return work_hours


class CleaningPrice(models.Model):
    """
    Holds all the cleaning prices for city-months-sessions permutations.

    :city: ForeignKey to the city table.
    :number_of_months: Number of months in a year the service is required for.
    :sessions_per_week: Number of days in a week the service is required for.
    :hourly_rate: Rate per hour for the given combination of
      city-months-sessions.
    """
    MONTHS_CHOICES = (
        (3, '3 Months'),
        (6, '6 Months'),
        (12, '12 Months'),
    )

    NUMBER_OF_SESSIONS = ((1, 'One'), (2, 'Two'), (3, 'Three'))

    city = models.ForeignKey(City, related_name='prices')
    number_of_months = models.IntegerField(
        choices=MONTHS_CHOICES, null=True, blank=True)
    sessions_per_week = models.IntegerField(
        choices=NUMBER_OF_SESSIONS, null=True, blank=True)
    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return "{} sessions per week at {} for {} months".format(
            self.sessions_per_week, self.city, self.number_of_months)

    def get_hours_per_session(self, extra_rooms=None, extras=None):
        return CleaningHour.objects.get().get_work_hours(
            extra_rooms=extra_rooms, extras=extras)

    def get_total_number_of_sessions(self, months=None, sessions=None):
        default_sessions_per_week = (self.sessions_per_week
                                     if self.sessions_per_week else 1)
        default_months = (self.number_of_months
                          if self.number_of_months else 0)
        sessions_per_week = sessions if sessions else default_sessions_per_week
        months = months if months else default_months
        return (sessions_per_week * 4 * months)

    def get_fee_per_month(self,
                          months=None,
                          sessions=None,
                          extra_rooms=None,
                          extras=None):
        total_sessions = self.get_total_number_of_sessions(
            months=months, sessions=sessions)
        hourly_rate = self.hourly_rate if self.hourly_rate else 1
        hours_per_session = self.get_hours_per_session(
            extra_rooms=extra_rooms, extras=extras)
        number_of_months = (self.number_of_months
                            if self.number_of_months else 1)
        fee_per_month = (total_sessions * hourly_rate * hours_per_session /
                         number_of_months)
        return fee_per_month
