""" RapData Spiders module """

import ratpy

from projects.rapdata.spiders import frap
from projects.rapdata.spiders import genius
from projects.rapdata.spiders import musique_urbaine

# ############################################################### #
# ############################################################### #


class Spiders(ratpy.SubSpider):

    name = 'rapdata.spiders'
    subspiders_cls = {
        'frap': frap.Frap,
        'genius': genius.Genius,
        'musique_urbaine': musique_urbaine.MusiqueUrbaine
    }

# ############################################################### #
# ############################################################### #
