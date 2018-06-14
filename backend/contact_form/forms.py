from django import forms

from . import models


class ContactForm(forms.ModelForm):

    class Meta:
        model = models.ContactRequest
        fields = ['name', 'email', 'phone', 'message', 'view']

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['phone'].required = True
