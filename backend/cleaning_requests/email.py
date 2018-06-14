from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def notify_new_cleaning_request(cleaning_request):
    ctx = {
        'name': cleaning_request.name,
        'email': cleaning_request.user_email,
        'address': cleaning_request.user_address,
        'date_requested': str(cleaning_request.first_visit.date()),
        'rooms': cleaning_request.num_bedrooms,
        'bathrooms': cleaning_request.num_bathrooms,
        'extras': cleaning_request.extras.all(),
        'calculated_hours': cleaning_request.num_hours,
        'calculated_quote': cleaning_request.calculated_quote
    }
    text_content = render_to_string(
        'cleaning_requests/email/new_cleaning_request.txt', ctx)
    send_mail(
        "{} ALERT: New Cleaning Request by {}".format(
            settings.EMAIL_SUBJECT_PREFIX, cleaning_request.user_email),
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        settings.ADMIN_EMAIL_RECIPIENTS,
    )
