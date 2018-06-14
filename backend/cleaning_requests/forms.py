from django import forms
from django.utils import timezone

from . import models
from . import email
from pricing.models import City, CleaningExtra, CleaningHour, CleaningPrice


class CleaningRequestFormStep1(forms.ModelForm):
    city = forms.ModelChoiceField(
        queryset=City.objects.filter(
            id__in=set(CleaningPrice.objects.all().values_list(
                'city__id', flat=True))),
        to_field_name='slug',
        empty_label=None)

    extras = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = models.CleaningRequest
        fields = ('city', 'num_bedrooms', 'num_bathrooms', 'extras',
                  'user_email', 'calculated_quote')
        fieldsets = (('', {
            'fields': (
                'city',
                'num_bedrooms',
                'num_bathrooms',
                'extras',
                'user_email',
            )
        }),)

    def __init__(self, *args, **kwargs):
        super(CleaningRequestFormStep1, self).__init__(*args, **kwargs)

        # Labels
        self.fields['city'].label = 'City'
        self.fields['num_bedrooms'].label = 'Number of bedrooms'
        self.fields['num_bathrooms'].label = 'Number of bathrooms'
        self.fields['user_email'].label = 'Your email address'
        self.fields['extras'].label = 'Extras'

        # Choices
        self.fields['extras'].choices = \
            [(item.slug, item.name) for item in CleaningExtra.objects.all() ]

        # Initials
        self.initial['city'] = City.objects.all().first().slug
        if kwargs.get('initial'):
            self.initial['extras'] = kwargs['initial'].get('extras')

    def save(self, *args, **kwargs):
        instance = super(CleaningRequestFormStep1, self).save(*args, **kwargs)
        city = City.objects.get(name=instance.city)
        instance.currency_code = city.currency_code
        instance.save()
        extras = self.cleaned_data.get('extras')
        if extras:
            for extra in CleaningExtra.objects.filter(slug__in=extras):
                models.CleaningRequestExtras.objects.create(
                    cleaning_request=instance,
                    name=extra.name,
                    hours=extra.hours)
        return instance


class CleaningRequestFormStep2(forms.ModelForm):
    currency_code = forms.CharField(max_length=3)
    num_hours = forms.DecimalField(disabled=True)
    calculated_quote = forms.DecimalField(disabled=True)

    class Meta:
        model = models.CleaningRequest
        fields = ('schedule', 'months', 'first_visit', 'name', 'zip',
                  'user_email', 'city', 'user_address', 'num_hours',
                  'calculated_quote', 'stripe_card', 'stripe_customer',
                  'currency_code')
        fieldsets = (('', {
            'fields': ('schedule', 'months', 'first_visit', 'name', 'zip',
                       'user_address', 'num_hours', 'calculated_quote')
        }),)

    def __init__(self, *args, **kwargs):
        if kwargs.get('data'):
            # This is a bit hacky:
            # We do have these two fields as form fields, but we don't really
            # want to treat them like form fields. What we save into the DB
            # should always be calculated based on the other fields, these two
            # fields are just for display purposes to the user, not for
            # submitting data. Therefore we pop them and add them back with
            # newly calculated values at the end of this function...
            kwargs.get('data').pop('num_hours')
            kwargs.get('data').pop('calculated_quote')

        super(CleaningRequestFormStep2, self).__init__(*args, **kwargs)

        currency_code = City.objects.get(
            name=kwargs['instance'].city).currency_code

        # Required
        self.fields['first_visit'].required = True
        self.fields['name'].required = True
        self.fields['zip'].required = True
        self.fields['user_address'].required = True

        # Labels
        self.fields['months'].label = 'Package'
        self.fields['name'].label = 'Your full name'
        self.fields['zip'].label = 'Your postal code'
        self.fields['user_address'].label = 'Your address'
        self.fields['num_hours'].label = 'Hours per session'
        self.fields[
            'calculated_quote'].label = 'Price per Month (in {})'.format(
                currency_code)

        # Placeholders
        self.fields['first_visit'].widget.attrs['placeholder'] = 'YYYY-MM-DD'
        self.fields['user_address'].widget.attrs[
            'placeholder'] = 'Street & Unit number'

        # Initials
        if self.data.get('schedule'):
            schedule = self.data.get('schedule')
        else:
            schedule = self.initial.get('schedule')
        if self.data.get('months'):
            months = self.data.get('months')
        else:
            months = self.initial.get('months')
        self.initial['currency_code'] = currency_code
        self.initial['num_hours'] = self.instance.get_num_hours(
            schedule=schedule, months=months)
        self.initial['calculated_quote'] = self.instance.get_calculated_quote(
            schedule=schedule, months=months)

        # ...adding back the popped fake-form-fields:
        if kwargs.get('data'):
            self.data['num_hours'] = self.initial.get('num_hours')
            self.data['calculated_quote'] = self.initial.get(
                'calculated_quote')

    def clean_first_visit(self):
        date = self.cleaned_data['first_visit']
        if date <= timezone.now():
            self.add_error('first_visit', 'Please enter a future date.')
        return date

    def save(self, *args, **kwargs):
        cleaning_request = super(CleaningRequestFormStep2, self).save(
            *args, **kwargs)
        email.notify_new_cleaning_request(cleaning_request)
        return cleaning_request
