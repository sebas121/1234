from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser


class InfoFactory(object):
    context = None

    def __init__(self, *args, **kwargs):
        self.context = RequestFactory().get('/')
        self.context.user = AnonymousUser()
        self.context.LANGUAGE_CODE = 'en'
