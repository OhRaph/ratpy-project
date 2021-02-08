""" WordData Spiders module """

import ratpy

from projects.worddata.spiders import dico2rue
from projects.worddata.spiders import dicodelazone

# ############################################################### #
# ############################################################### #


class Spiders(ratpy.SubSpider):

    name = 'worddata.spiders'
    subspiders_cls = {
        'dico2rue': dico2rue.Dico2Rue,
        'dicodelazone': dicodelazone.DicoDeLaZone
    }

# ############################################################### #
# ############################################################### #
