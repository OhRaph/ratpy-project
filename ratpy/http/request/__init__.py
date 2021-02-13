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


class Request(scrapy.Request):

    """ Ratpy Request class """

    # ####################################################### #
    # ####################################################### #

    timestamp = None

    def __init__(self, *args, url='', timestamp=None, **kwargs):
        scrapy.Request.__init__(self, url, *args, **kwargs)
        self.timestamp = timestamp if timestamp else None

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

        names = ['method', 'headers', 'body', 'cookies', 'meta', 'flags', 'encoding', 'priority', 'timestamp', 'dont_filter', 'cb_kwargs']
        attributes = {name: getattr(self, name, None) for name in names}
        attributes['url'] = URL(self.url)

        return attributes

    def replace(self, **kwargs):

        if kwargs != {}:
            for x in ['url', 'method', 'headers', 'body', 'cookies', 'meta', 'flags', 'encoding', 'priority', 'timestamp', 'dont_filter', 'cb_kwargs', 'callback', 'errback']:
                kwargs.setdefault(x, getattr(self, x))
            cls = kwargs.pop('cls', self.__class__)
            request = cls(**kwargs)
        else:
            request = self

        return request

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
