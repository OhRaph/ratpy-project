""" RapData module """

import ratpy

from projects.rapdata.spiders import Spiders

# ############################################################### #
# ############################################################### #

DEFAULT_URL = ''
DEFAULT_LINKER = 'True'


class RapData(ratpy.Spider):

    """ RapData class """

    name = 'rapdata'
    subspiders_cls = Spiders

    def __init__(self, *args, url=DEFAULT_URL, linker=DEFAULT_LINKER, **kwargs):
        self.linker = (linker == 'True')
        ratpy.Spider.__init__(self, *args, start_url=url, **kwargs)

# ############################################################### #
# ############################################################### #
