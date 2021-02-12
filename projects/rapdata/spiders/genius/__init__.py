""" RapData Genius Spiders module """

import ratpy

from projects.rapdata.spiders.genius import api, ui


# ############################################################### #
# ############################################################### #


class Genius(ratpy.SubSpider):

    name = 'rapdata.spiders.genius'
    activated = True
    subspiders_cls = {
        'api': api.GeniusAPI,
        'ui': ui.GeniusUI
    }

    def process_output(self, url, item, *args, **kwargs):
        item['website'] = 'genius'
        return item

# ############################################################### #
# ############################################################### #
