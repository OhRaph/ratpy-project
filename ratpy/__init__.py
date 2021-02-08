""" Ratpy module """

import sys
if sys.version_info < (3, 5):
    print("Ratpy requires Python 3.5")
    sys.exit(1)
del sys

from ratpy.spider import Spider, SubSpider
from ratpy.link import Link, Linker
from ratpy.item import Item
from ratpy.field import Field
from ratpy.utils import normalize, resources_directory, work_directory, log_directory

from ratpy.http.url import URL
from ratpy.http.request import Request, IgnoreRequest, PostponeRequest
from ratpy.http.response import Response, IgnoreResponse, PostponeResponse

__all__ = [
    'Spider', 'SubSpider', 'Link', 'Linker', 'URL', 'Item', 'Field',
    'Request', 'IgnoreRequest', 'PostponeRequest',
    'Response', 'IgnoreResponse', 'PostponeResponse',
    'normalize'
    ]


# ############################################################### #
# ############################################################### #
