""" RapData GeniusUI Parser module """

import re
import bs4

import ratpy

# ############################################################### #
# ############################################################### #


class Parser(ratpy.Linker):

    # ####################################################### #
    # ####################################################### #

    def get_id(self, content):

        tmp = content.find('meta', content=re.compile('^genius://songs/[0-9]*'))
        return tmp.get('content', '').split('/')[-1] if tmp else ''

    def get_api(self, content):

        tmp = self.get_id(content)
        return '/songs/'+tmp if tmp else ''

    def get_url(self, content):

        tmp = content.find('meta', content=re.compile('^https://genius\\.com/.*'))
        return tmp['content'] if tmp else ''

    # ####################################################### #

    def parse_info(self, content, *args, **kwargs):

        self.add_link(self.get_api(content), *args, **kwargs)
        return {
            'id': self.get_id(content),
            'api': self.get_api(content),
            'url': self.get_url(content)
        }

    def parse_title(self, content):

        return content.find('h1').getText()

    # ####################################################### #

    def find_parse_lyrics_method(self, content):
        try:
            content.find('div', class_='lyrics').getText()
            return 1
        except:
            content.find('div', id='lyrics').findNext('div').findNext('div').getText()
            return 2

    def find_lyrics_method_1(self, content):
        return content.find('div', class_='lyrics')

    def find_lyrics_method_2(self, content):
        return content.find('div', id='lyrics').findNext('div').findNext('div')

    # ####################################################### #

    def parse_lyrics(self, content):

        if self.find_parse_lyrics_method(content) == 1:
            return self.parse_lyrics_method_1(self.find_lyrics_method_1(content))
        if self.find_parse_lyrics_method(content) == 2:
            return self.parse_lyrics_method_2(self.find_lyrics_method_2(content))

    def parse_lyrics_method_1(self, content):
        return content.getText()

    def parse_lyrics_method_2(self, content):
        for x in content.findAll("br"):
            x.replaceWith("\n")
        return content.getText()

    # ####################################################### #

    def parse_lyrics_annotations(self, content, *args, **kwargs):

        if self.find_parse_lyrics_method(content) == 1:
            return self.parse_lyrics_annotations_method_1(self.find_lyrics_method_1(content))
        if self.find_parse_lyrics_method(content) == 2:
            return self.parse_lyrics_annotations_method_2(self.find_lyrics_method_2(content))

    def parse_lyrics_annotations_method_1(self, content, *args, **kwargs):

        def annotation_api_path(content):
            return 'http://api.genius.com/annotations/' + content.get('annotation-fragment', '')

        annotations = []
        blocks = content.find_all('p') if content else []
        for block in blocks:
            for punch in block:
                if isinstance(punch, bs4.element.NavigableString):
                    tmp = str(punch.encode('utf-8').decode('utf-8')).strip('\n')
                    if tmp != '':
                        annotations.append(tmp)
                if isinstance(punch, bs4.element.Tag):
                    if punch.name == 'br':
                        annotations.append('\n')
                    if punch.name == 'a':
                        if 'referent' in punch.get('class', []):
                            self.add_link(annotation_api_path(punch), *args, **kwargs)
                            annotations.append([punch.get_text(), annotation_api_path(punch)])
                        else:
                            self.add_link(punch.get('href', ''), *args, **kwargs)
        return annotations

    def parse_lyrics_annotations_method_2(self, content, *args, **kwargs):

        def annotation_api_path(content):
            return 'http://api.genius.com/annotations/' + content.get('href', '').split('/')[1]

        annotations = []
        blocks = content.findChildren('div', recursive=False)
        for block in blocks:
            for punch in block:
                if isinstance(punch, bs4.element.NavigableString):
                    tmp = str(punch.encode('utf-8').decode('utf-8')).strip('\n')
                    if tmp != '':
                        annotations.append(tmp)
                if isinstance(punch, bs4.element.Tag):
                    if punch.name == 'br':
                        annotations.append('\n')
                    if punch.name == 'a':
                        for x in punch.find_all("br"):
                            x.replaceWith("\n")
                        self.add_link(annotation_api_path(punch), *args, **kwargs)
                        annotations.append([punch.get_text(), annotation_api_path(punch)])
        return annotations

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
