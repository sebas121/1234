DEBUG = True
FULL_DOMAIN_DJANGO = 'https://{{ nginx_server_name }}'
ALLOWED_HOSTS = ['{{ project_domain }}', '{{ host_ip }}', 'localhost']
STATIC_ROOT = '/home/{{ deploy_user }}/project_assets/static/'
MEDIA_ROOT = '/home/{{ deploy_user }}/project_assets/media/'

ADMIN_EMAIL_RECIPIENTS = ['info@ddiy-solutions.com']
DEFAULT_FROM_EMAIL = 'info@ddiy-solutions.com'
EMAIL_SUBJECT_PREFIX = ''
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
ANYMAIL = {
    # This is the sandbox API key, make sure to set the real one on the server
    "MAILGUN_API_KEY": "key-673babe583668f6a1e0377d19cef92e5",
}
