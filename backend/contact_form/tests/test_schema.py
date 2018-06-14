import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db

from django.core import mail

from backend.utils import InfoFactory

from .. import schema
from .. import models


class TestContactFormMutation(object):

    def test_mutation(self, mocker):
        m = schema.ContactFormMutation()
        info = InfoFactory()
        res = m.mutate(None, info, **{})
        assert res.status == 400, 'Should return form errors if no data is given'

        data = {
            'name': 'Test',
            'email': 'test@example.com',
            'message': 'Test',
        }
        res = m.mutate(None, info, **data)
        assert res.status == 200, 'Should return 200 if all data is given'
        assert models.ContactRequest.objects.all().count() == 1, (
            'Should save the ContactRequest into the DB')
        assert len(mail.outbox) == 1, 'Should send an admin notification email'
