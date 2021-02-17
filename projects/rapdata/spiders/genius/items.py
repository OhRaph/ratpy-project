"""  RapData Genius Items module """

import ratpy

# ############################################################### #
# ############################################################### #


class Artist(ratpy.Item):

    class Names(ratpy.Field):
        main = ratpy.Field()
        others = ratpy.Field()

    class Social(ratpy.Field):

        class Networks(ratpy.Field):
            facebook = ratpy.Field()
            instagram = ratpy.Field()
            twitter = ratpy.Field()

        followers = ratpy.Field()
        networks = Networks()

    class Songs(ratpy.Item):
        page = ratpy.Field()
        songs = ratpy.Field()

    names = Names()
    description = ratpy.Field()
    social = Social()
    verified = ratpy.Field()
    picture = ratpy.Field()

# ############################################################### #


class Album(ratpy.Item):

    class Titles(ratpy.Field):
        main = ratpy.Field()
        others = ratpy.Field()

    class Artists(ratpy.Field):
        main = ratpy.Field()
        others = ratpy.Field()

    titles = Titles()
    description = ratpy.Field()
    release = ratpy.Field()
    cover = ratpy.Field()
    artists = Artists()

# ############################################################### #


class Music(ratpy.Item):

    class Titles(ratpy.Field):
        main = ratpy.Field()
        others = ratpy.Field()

    class Artists(ratpy.Field):
        main = ratpy.Field()
        others = ratpy.Field()

    class Lyrics(ratpy.Item):

        class Annotation(ratpy.Item):
            body = ratpy.Field()
            pinned = ratpy.Field()
            state = ratpy.Field()

        title = ratpy.Field()
        lyrics = ratpy.Field()
        annotations = ratpy.Field()

    titles = Titles()
    description = ratpy.Field()
    release = ratpy.Field()
    artists = Artists()
    album = ratpy.Field()
    status = ratpy.Field()
    relations = ratpy.Field()

# ############################################################### #
# ############################################################### #
