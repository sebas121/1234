from django.http import QueryDict


def get_query_dict(query_string):
    if query_string is None:
        query_string = ''
    filters = u'{}'.format(query_string.replace('?', '')).encode('utf-8')
    query_dict = QueryDict(
        query_string=filters, mutable=True, encoding='utf-8')
    result = query_dict.dict()
    if query_dict.get('extras'):
        result['extras'] = query_dict.getlist('extras')

    return result
