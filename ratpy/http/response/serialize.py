""" Ratpy Response Serialization module """

from ratpy.utils import to_unicode, load_object
from ratpy.http.response import Response
from ratpy.http.request.serialize import request_to_dict, request_from_dict

# ############################################################### #
# ############################################################### #


def response_to_dict(response, spider=None):

    if response is None:
        return None

    res = {
        'url': to_unicode(response.url),
        'status': response.status,
        'headers': dict(response.headers),
        'request': request_to_dict(response.request, spider),
        'body': response.body,
        'flags': response.flags,
        'certificate': response.certificate,
        'ip_adress': response.ip_adress
    }

    if type(response) is not Response:  # pylint: disable=unidiomatic-typecheck
        res['_class'] = response.__module__ + '.' + response.__class__.__name__
    return res

# ############################################################### #


def response_from_dict(dic, spider=None):

    if dic is None or dic == {}:
        return None

    response_cls = load_object(dic['_class']) if '_class' in dic else Response
    return response_cls(
        url=to_unicode(dic['url']),
        status=dic['status'],
        headers=dic['headers'],
        request=request_from_dict(dic['request'], spider),
        body=dic['body'],
        flags=dic.get('flags'),
        certificate=dic['certificate'],
        ip_adress=dic['ip_adress']
    )

# ############################################################### #
# ############################################################### #
