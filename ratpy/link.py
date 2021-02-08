""" Ratpy Link module """

from collections.abc import Iterable
from ratpy.http.url import URL

__all__ = ['Link', 'Linker']

# ############################################################### #
# ############################################################### #


class Link:

    """ Ratpy Link class """

    # ####################################################### #
    # ####################################################### #

    url = None
    args = None
    kwargs = None

    # ####################################################### #

    def __init__(self, url, *args, **kwargs):

        self.url = URL(url)
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return [self.url, self.args, self.kwargs].__str__()

    def __repr__(self):
        return {'url': self.url, 'args': self.args, 'kwargs': self.kwargs}.__repr__()

    # ####################################################### #

    @staticmethod
    def create(value, *args, **kwargs):
        if value is None:
            pass
        elif isinstance(value, Link):
            yield value
        elif isinstance(value, str):
            yield Link(value, *args, **kwargs)
        elif isinstance(value, Iterable):
            for _value in value:
                yield from Link.create(_value, *args, **kwargs)
        else:
            yield Link(str(value), *args, **kwargs)

    @property
    def infos(self):
        return {'url': self.url.infos, 'args': self.args, 'kwargs': self.kwargs}

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


class Linker:

    # ####################################################### #
    # ####################################################### #

    links = None

    # ####################################################### #

    def __init__(self):

        self.links = []

    # ####################################################### #
    # ####################################################### #

    def add_link(self, link, *args, linker=True, **kwargs):
        if linker:
            if isinstance(link, (URL, str)):
                self.links.append(Link(link, *args, **kwargs))
            elif isinstance(link, Link):
                self.links.append(link)
            else:
                pass

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
