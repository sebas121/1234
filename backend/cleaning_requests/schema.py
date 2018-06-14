import stripe
import graphene
import simplejson as json

from decimal import Decimal
from graphene_django.types import DjangoObjectType
from django_form_serializer import DjangoFormSerializer

from django.conf import settings

from . import forms
from . import models
from . import utils


def create_stripe_customer(token):
    stripe.api_key = settings.STRIPE_API_KEY

    customer = stripe.Customer.create(source=token)
    stripe_customer_id = customer.get('id')
    stripe_card_id = customer.default_source

    return stripe_customer_id, stripe_card_id


def create_stripe_charge(ccy, amount, stripe_customer_id, stripe_card_id):
    stripe.Charge.create(
        amount=int(Decimal(amount) * 100),
        currency=ccy,
        customer=stripe_customer_id,
        source=stripe_card_id,
    )


class CleaningRequestType(DjangoObjectType):

    class Meta:
        model = models.CleaningRequest


class CleaningRequestMutation(graphene.Mutation):

    class Arguments:
        data = graphene.String()

    status = graphene.Int()
    form_errors = graphene.String()
    form = graphene.String()
    cleaning_request = graphene.Field(CleaningRequestType)

    @staticmethod
    def mutate(root, info, **args):
        submit = args.get('submit', 'false')
        data = utils.get_query_dict(args.get('data'))
        form = forms.CleaningRequestFormStep1(data=data)

        if not form.is_valid():
            form_dict = DjangoFormSerializer().parse(form)
            return CleaningRequestMutation(
                status=400,
                form_errors=json.dumps(form.errors),
                form=json.dumps(form_dict),
                cleaning_request=None)

        cleaning_request = form.save()
        form_dict = DjangoFormSerializer().parse(form)
        return CleaningRequestMutation(
            status=200,
            form_errors=None,
            form=json.dumps(form_dict),
            cleaning_request=cleaning_request)


class CleaningRequestPaymentMutation(graphene.Mutation):

    class Arguments:
        data = graphene.String()
        submit = graphene.String()

    status = graphene.Int()
    form_errors = graphene.String()
    form = graphene.String()
    is_payment_successful = graphene.Boolean()
    cleaning_request = graphene.Field(CleaningRequestType)

    @staticmethod
    def mutate(root, info, **args):
        submit = args.get('submit', 'false')
        data = utils.get_query_dict(args.get('data'))
        token = data.get('stripeToken', None)
        is_payment_successful = False

        if token:
            stripe_customer_id, stripe_card_id = create_stripe_customer(token)
            data['stripe_customer'] = stripe_customer_id
            data['stripe_card'] = stripe_card_id

        cleaning_request_id = data.get('id')
        cleaning_request = models.CleaningRequest.objects.get(
            id=cleaning_request_id)
        form = forms.CleaningRequestFormStep2(
            data=data, instance=cleaning_request)

        if not form.is_valid():
            form_json = DjangoFormSerializer().parse(form)
            return CleaningRequestPaymentMutation(
                status=400,
                form_errors=json.dumps(form.errors),
                form=json.dumps(form_json),
                is_payment_successful=is_payment_successful,
                cleaning_request=None)

        if submit == 'true':
            cleaning_request = form.save()
            if token:
                try:
                    create_stripe_charge(cleaning_request.currency_code,
                                         cleaning_request.calculated_quote,
                                         stripe_customer_id, stripe_card_id)
                except stripe.error.CardError as e:
                    body = e.json_body
                    err = body.get('error', {})
                    error_message = \
                        ('Failed to charge card {} for customer {}.'
                         'Error message: {}').format(
                                        stripe_card_id, stripe_customer_id,
                                        err.get('message'))
                    cleaning_request.status = 'failed'
                    cleaning_request.stripe_error = error_message
                    cleaning_request.save()
                    return CleaningRequestMutation(
                        status=400,
                        form_errors=json.dumps({
                            'non_field_errors': [
                                'Your card has been declined. Please try again.'
                            ]
                        }),
                        form=json.dumps(form_json),
                        is_payment_successful=is_payment_successful,
                        cleaning_request=cleaning_request)
                cleaning_request.status = 'paid'
                cleaning_request.save()
            is_payment_successful = True
            if token is None:
                cleaning_request.status = 'cash'
                cleaning_request.save()
        else:
            cleaning_request = None

        form_json = DjangoFormSerializer().parse(form)
        return CleaningRequestPaymentMutation(
            status=200,
            form_errors=None,
            form=json.dumps(form_json),
            is_payment_successful=is_payment_successful,
            cleaning_request=cleaning_request)


class Query(object):
    get_cleaning_request_form = graphene.Field(graphene.String)
    get_cleaning_request_payment_form = graphene.Field(
        graphene.String, id=graphene.String())

    def resolve_get_cleaning_request_form(self, info, **args):
        form = forms.CleaningRequestFormStep1()
        form_json = DjangoFormSerializer().parse(form)
        return json.dumps(form_json)

    def resolve_get_cleaning_request_payment_form(self, info, **args):
        id = args.get('id', None)
        cleaning_request = models.CleaningRequest.objects.get(id=id)
        form = forms.CleaningRequestFormStep2(instance=cleaning_request)
        form_json = DjangoFormSerializer().parse(form)
        return json.dumps(form_json)


class Mutation(object):
    create_cleaning_request = CleaningRequestMutation.Field()
    create_cleaning_request_payment = CleaningRequestPaymentMutation.Field()
