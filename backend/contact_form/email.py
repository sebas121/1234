from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse


def send_admin_new_contact_request(contact_request):
    admin_url = reverse(
        'admin:contact_form_contactrequest_change', args=(contact_request.pk,))
    ctx = {
        'admin_url': admin_url,
        'name': contact_request.name,
        'email': contact_request.email,
        'phone': contact_request.phone,
        'view': contact_request.view,
        'message': contact_request.message,
        'date_created': str(contact_request.date_created),
        'FULL_DOMAIN': settings.FULL_DOMAIN_DJANGO,
    }
    text_content = render_to_string(
        'contact_form/email/admin_new_contact_request.txt', ctx)
    send_mail(
        "{} ALERT: New Contact Request by {}".format(
            settings.EMAIL_SUBJECT_PREFIX, contact_request.email),
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        settings.ADMIN_EMAIL_RECIPIENTS,
    )
