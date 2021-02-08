""" WordData DicoDeLaZone Items module """

import ratpy

# ############################################################### #
# ############################################################### #


class Word(ratpy.Item):

    class Usage(ratpy.Item):
        word = ratpy.Field()
        type = ratpy.Field()
        meanings = ratpy.Field()

    class Meaning(ratpy.Item):
        definition = ratpy.Field()
        synonyms = ratpy.Field()
        examples = ratpy.Field()

    class Example(ratpy.Item):
        citation = ratpy.Field()
        author = ratpy.Field()
        container1 = ratpy.Field()
        container2 = ratpy.Field()
        date = ratpy.Field()

    etymology = ratpy.Field()
    usages = ratpy.Field()

# ############################################################### #
# ############################################################### #
