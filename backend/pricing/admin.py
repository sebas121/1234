from django.contrib import admin

from . import models


class CityAdmin(admin.ModelAdmin):
    models = models.City


class CleaningPriceAdmin(admin.ModelAdmin):
    models = models.CleaningPrice
    list_display = [
        'city', 'number_of_months', 'sessions_per_week', 'hourly_rate',
        'hours_per_session', 'weeks_per_month', 'total_number_of_sessions',
        'fee_per_month'
    ]
    readonly_fields = [
        'hours_per_session', 'weeks_per_month', 'total_number_of_sessions',
        'fee_per_month'
    ]
    search_fields = [
        'city__name',
    ]

    def hours_per_session(self, obj):
        return obj.get_hours_per_session()

    def weeks_per_month(self, obj):
        return 4

    def total_number_of_sessions(self, obj):
        return obj.get_total_number_of_sessions()

    def fee_per_month(self, obj):
        return obj.get_fee_per_month()


class CleaningHourAdmin(admin.ModelAdmin):
    models = models.CleaningHour


class CleaningExtraAdmin(admin.ModelAdmin):
    models = models.CleaningExtra
    list_display = ['name', 'hours']


admin.site.register(models.City, CityAdmin)
admin.site.register(models.CleaningPrice, CleaningPriceAdmin)
admin.site.register(models.CleaningHour, CleaningHourAdmin)
admin.site.register(models.CleaningExtra, CleaningExtraAdmin)
