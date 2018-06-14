import json

import graphene

from . import email
from . import forms


class ContactFormMutation(graphene.Mutation):

    class Arguments:
        name = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        message = graphene.String()
        view = graphene.String()

    status = graphene.Int()
    form_errors = graphene.String()

    @staticmethod
    def mutate(root, info, **args):
        form = forms.ContactForm(data=args)
        if not form.is_valid():
            return ContactFormMutation(
                status=400, form_errors=json.dumps(form.errors))
        instance = form.save()
        email.send_admin_new_contact_request(instance)
        return ContactFormMutation(status=200, form_errors=None)


class Mutation(object):
    contact_form = ContactFormMutation.Field()
