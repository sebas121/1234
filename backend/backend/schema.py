import graphene

import cleaning_requests.schema
import contact_form.schema
import pricing.schema


class Mutations(contact_form.schema.Mutation,
                cleaning_requests.schema.Mutation, graphene.ObjectType):
    pass


class Queries(cleaning_requests.schema.Query, pricing.schema.Query,
              graphene.ObjectType):
    pass


schema = graphene.Schema(query=Queries, mutation=Mutations)
