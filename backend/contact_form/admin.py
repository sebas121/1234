from django.contrib import admin

from . import models


class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ['date_created', 'email', 'status', 'view']
    list_filter = ['status', 'view']
    search_fields = ['name', 'email', 'phone', 'admin_notes']


admin.site.register(models.ContactRequest, ContactRequestAdmin)
