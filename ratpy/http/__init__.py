""" Ratpy HTTP module """

from ratpy.http.request import Request, IgnoreRequest
from ratpy.http.response import Response, IgnoreResponse

__all__ = [
    'Request', 'IgnoreRequest',
    'Response', 'IgnoreResponse'
    ]
