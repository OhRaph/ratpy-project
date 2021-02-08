""" Rapdata MusiqueUrbaine Items module """

import ratpy

# ############################################################### #
# ############################################################### #


class ArtistOrGroup(ratpy.Item):

    class Names(ratpy.Field):
        main = ratpy.Field()
        others = ratpy.Field()

    class Networks(ratpy.Field):
        facebook = ratpy.Field()
        instagram = ratpy.Field()
        twitter = ratpy.Field()
        youtube = ratpy.Field()
        bandcamp = ratpy.Field()
        soundcloud = ratpy.Field()
        snapchat = ratpy.Field()
        website = ratpy.Field()

    names = Names()
    description = ratpy.Field()
    origin = ratpy.Field()
    networks = Networks()
    picture = ratpy.Field()
    groups = ratpy.Field()
    streaming = ratpy.Field()


class Artist(ArtistOrGroup):

    class Birth(ratpy.Field):
        name = ratpy.Field()
        date = ratpy.Field()

    birth = Birth()


class Group(ArtistOrGroup):

    class Activity(ratpy.Field):
        begin = ratpy.Field()
        end = ratpy.Field()

    activity = Activity()
    members = ratpy.Field()

# ############################################################### #


class Album(ratpy.Item):

    title = ratpy.Field()
    release = ratpy.Field()
    format = ratpy.Field()
    cover = ratpy.Field()
    songs = ratpy.Field()
    streaming = ratpy.Field()

# ############################################################### #


class Media(ratpy.Item):
    title = ratpy.Field()
    type = ratpy.Field()
    url = ratpy.Field()

# ############################################################### #
# ############################################################### #
