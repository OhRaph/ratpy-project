""" Ratpy Request module """

from collections.abc import Iterable
from urllib.parse import urljoin

import scrapy

from ratpy.http.url import URL

__all__ = ['Request', 'IgnoreRequest', 'PostponeRequest']

# ############################################################### #
# ############################################################### #


class IgnoreRequest(scrapy.exceptions.IgnoreRequest):

    """ Ratpy Ignore Request class """


class PostponeRequest(Exception):

    """ Ratpy Postpone Request class """

# ############################################################### #


class Request(scrapy.http.Request):

    """ Ratpy Request class """

    # ####################################################### #
    # ####################################################### #

    def __init__(self, *args, url='', **kwargs):
        scrapy.http.Request.__init__(self, url, *args, **kwargs)

    @staticmethod
    def create(value, *args, origin='', **kwargs):

        if isinstance(origin, URL):
            origin = origin.path

        if value is None:
            pass
        elif isinstance(value, Request):
            yield value
        elif isinstance(value, str):
            yield Request(*args, url=urljoin(origin, value), **kwargs)
        elif isinstance(value, Iterable):
            for _value in value:
                yield from Request.create(_value, *args, origin=origin, **kwargs)
        else:
            yield from Request.create(value.url, *value.args, *args, origin=origin, **value.kwargs, **kwargs)

    def get_attributes(self):

        names = ['method', 'headers', 'body', 'cookies', 'meta', 'flags', 'encoding', 'priority', 'dont_filter', 'cb_kwargs']
        attributes = {name: getattr(self, name, None) for name in names}
        attributes['url'] = URL(self.url)

        return attributes

    def replace(self, **kwargs):

        if kwargs != {}:
            request = scrapy.http.Request.replace(self, **kwargs)
        else:
            request = self

        return request

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
