""" Ratpy Item module """

import scrapy

from ratpy.field import Field

__all__ = ['Item']

# ############################################################### #
# ############################################################### #


class Item(scrapy.Item):

    website = Field()
    infos = Field()
    pipeline = Field()

    _file_urls = Field()
    _file_results = Field()

    _image_urls = Field()
    _image_results = Field()

# ############################################################### #
# ############################################################### #
