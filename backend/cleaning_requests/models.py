from django.db import models
from django.db.models import Sum

from pricing.models import CleaningHour, CleaningPrice


class CleaningRequestExtras(models.Model):
    cleaning_request = models.ForeignKey(
        'cleaning_requests.CleaningRequest', related_name='extras')
    name = models.CharField(max_length=128)
    hours = models.IntegerField()

    def __str__(self):
        return "Extra {} for {} hours".format(self.name, self.hours)


class CleaningRequest(models.Model):
    STATUS_CHOICES = (
        ('cash', 'Cash'),
        ('failed', 'Failed'),
        ('paid', 'Paid'),
        ('pending', 'Pending'),
    )

    MONTHS_CHOICES = (
        (3, '3 Months'),
        (6, '6 Months'),
        (12, '12 Months'),
    )

    NUMBER_OF_SESSIONS = ((1, 'Once per week'), (2, 'Twice per week'),
                          (3, 'Three times per week'))
    city = models.CharField(max_length=128)
    currency_code = models.CharField(max_length=3, blank=True, null=True)
    name = models.CharField(blank=True, null=True, max_length=128)
    zip = models.CharField(blank=True, null=True, max_length=128)
    schedule = models.IntegerField(choices=NUMBER_OF_SESSIONS, default=1)
    months = models.IntegerField(choices=MONTHS_CHOICES, default=3)
    num_bedrooms = models.IntegerField()
    num_bathrooms = models.IntegerField()
    num_hours = models.DecimalField(
        blank=True,
        null=True,
        max_digits=4,
        decimal_places=2,
    )
    first_visit = models.DateTimeField(blank=True, null=True)
    user_email = models.EmailField()
    user_address = models.TextField(blank=True, null=True)
    calculated_quote = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    admin_notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        blank=True,
        null=True,
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending')
    stripe_card = models.CharField(max_length=256, blank=True)
    stripe_customer = models.CharField(max_length=256, blank=True)
    stripe_error = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return "{} requests at {}. Email: {}".format(self.name, self.city,
                                                     self.user_email)

    def get_num_hours(self, schedule=None, months=None):
        """
        Returns the calculated number of hours per session for this instance.

        Sometimes we would like to calculate the hours based on values that
        the user has selected in the form (which are not written to the DB
        yet). For this case, we may pass in override values into this function.

        """
        # Initiating various values ===========================================
        if schedule is None:
            schedule = self.schedule
        if months is None:
            months = self.months
        extras_hours = self.extras.all().aggregate(
            Sum('hours'))['hours__sum'] or 0
        try:
            cleaning_hour = CleaningHour.objects.get()
        except CleaningHour.DoesNotExist:
            raise Exception('ERROR: Could not find a CleaningHour instance.')

        # Doing the actual calculation ========================================
        rooms_requested = self.num_bedrooms + self.num_bathrooms
        extra_rooms = max(rooms_requested - cleaning_hour.min_rooms, 0)

        work_hours = cleaning_hour.min_hours
        if extra_rooms:
            work_hours += extra_rooms * cleaning_hour.increment
        work_hours += extras_hours
        return work_hours

    def get_calculated_quote(self, schedule=None, months=None):
        """
        Returns the calculated quote per month for this instance.

        Sometimes we would like to calculate quote based on values that
        the user has selected in the form (which are not written to the DB
        yet). For this case, we may pass in override values into this function.

        """
        if schedule is None:
            schedule = self.schedule
        if months is None:
            months = self.months
        cleaning_price = CleaningPrice.objects.get(
            city__name=self.city,
            sessions_per_week=schedule,
            number_of_months=months)

        work_hours_per_session = self.get_num_hours(
            schedule=schedule, months=months)
        # hours per session * sessions per week * 4 weeks per mohth
        work_hours_per_month = work_hours_per_session * int(schedule) * 4
        fee_per_month = cleaning_price.hourly_rate * work_hours_per_month
        return round(fee_per_month, 2)
