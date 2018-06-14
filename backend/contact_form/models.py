from django.db import models

STATUS_CHOICES = [
    ['pending', 'Pending'],
    ['in_progress', 'In Progress'],
    ['done', 'Done'],
]


class ContactRequest(models.Model):
    name = models.CharField(max_length=1024)
    email = models.EmailField(max_length=1024)
    phone = models.CharField(max_length=1024, blank=True)
    message = models.TextField()
    view = models.CharField(max_length=4000, blank=True)
    admin_notes = models.TextField()
    status = models.CharField(
        choices=STATUS_CHOICES, default='pending', max_length=256)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
