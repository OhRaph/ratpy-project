""" Ratpy Response module """

import scrapy

__all__ = ['Response', 'IgnoreResponse', 'PostponeResponse']

# ############################################################### #
# ############################################################### #


class IgnoreResponse(scrapy.exceptions.IgnoreRequest):

    """ Ratpy Ignore Response class """

# ############################################################### #


class PostponeResponse(scrapy.exceptions.IgnoreRequest):

    """ Ratpy Postpone Response class """

# ############################################################### #


class Response(scrapy.http.TextResponse):

    """ Ratpy Response class """

    # ####################################################### #
    # ####################################################### #

    def __init__(self, *args, **kwargs):

        scrapy.http.TextResponse.__init__(self, *args, **kwargs)

    def get_attributes(self):

        names = ['status', 'headers', 'body', 'request', 'flags', 'certificate']
        attributes = {name: getattr(self, name, None) for name in names}

        return attributes

    def replace(self, **kwargs):

        if kwargs != {}:
            if 'body' in kwargs and isinstance(kwargs['body'], str):
                kwargs['body'] = kwargs['body'].encode(self.encoding)
            response = scrapy.http.TextResponse.replace(self, **kwargs)
        else:
            response = self

        return response

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
