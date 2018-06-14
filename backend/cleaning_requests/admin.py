from django.contrib import admin

from . import models


class CleaningRequestExtrasInline(admin.TabularInline):
    model = models.CleaningRequestExtras


class CleaningRequestAdmin(admin.ModelAdmin):
    models = models.CleaningRequest
    list_display = [
        'created_at', 'user_email', 'city', 'schedule', 'months',
        'num_bedrooms', 'num_bathrooms', 'first_visit', 'calculated_quote',
        'currency_code', 'status'
    ]

    list_filter = [
        'status', 'city', 'schedule', 'months', 'num_bedrooms',
        'num_bathrooms', 'currency_code'
    ]

    search_fields = ['user_email', 'user_address']

    date_hierarchy = 'created_at'

    inlines = [
        CleaningRequestExtrasInline,
    ]


admin.site.register(models.CleaningRequest, CleaningRequestAdmin)
