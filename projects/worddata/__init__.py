""" WordData module """

import ratpy

from projects.worddata.spiders import Spiders

# ############################################################### #
# ############################################################### #

DEFAULT_URL = ''
DEFAULT_LINKER = 'True'


class WordData(ratpy.Spider):

    """ WordData class """

    name = 'worddata'
    subspiders_cls = Spiders

    def __init__(self, *args, url=DEFAULT_URL, linker=DEFAULT_LINKER, **kwargs):
        self.linker = (linker == 'True')
        ratpy.Spider.__init__(self, *args, start_url=url, **kwargs)

# ############################################################### #
# ############################################################### #
