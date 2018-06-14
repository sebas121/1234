import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db

from .. import forms


class TestContactForm(object):

    def test_form(self):
        form = forms.ContactForm()
        assert form.is_valid(
        ) == False, 'Should be invalid if no data is given'

        data = {
            'name': 'Test',
            'email': 'test@example.com',
            'message': 'Test',
        }
        form = forms.ContactForm(data=data)
        assert form.is_valid() == True, 'Should be valid if all data is given'
        instance = form.save()
        assert instance.pk, 'Should return the saved instance'
