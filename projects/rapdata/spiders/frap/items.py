""" RapData Frap Items module """

import ratpy

# ############################################################### #
# ############################################################### #


class Album(ratpy.Item):

    title = ratpy.Field()
    artist = ratpy.Field()
    notation = ratpy.Field()
    release = ratpy.Field()
    cover = ratpy.Field()
    songs = ratpy.Field()

# ############################################################### #
# ############################################################### #
