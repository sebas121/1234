import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestContactRequest(object):

    def test_instance(self):
        obj = mixer.blend('contact_form.ContactRequest')
        assert obj.pk > 0
