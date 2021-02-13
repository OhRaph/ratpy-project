""" RapData GeniusAPI Parser module """

import ratpy

# ############################################################### #
# ############################################################### #


class Parser(ratpy.Linker):

    # ####################################################### #
    # ####################################################### #

    def get_id(self, content):

        return '{}'.format(content['id']) if content is not None and 'id' in content else None

    def get_api(self, content):

        return content['api_path'] if content is not None and 'api_path' in content else None

    def get_url(self, content):

        return content['url'] if content is not None and 'url' in content else None

    def get_href(self, content):

        return content['href'] if content is not None and 'href' in content else None

    def get_name(self, content):

        return ratpy.normalize(content['name']) if content is not None and 'name' in content else None

    # ####################################################### #

    def parse_info(self, content, *args, **kwargs):

        self.add_link(self.get_api(content), *args, **kwargs)
        return {
            'id': self.get_id(content),
            'api': self.get_api(content),
            'url': self.get_url(content)
        }

    def parse_url(self, content, *args, **kwargs):
        return self.get_url(content)

    # ####################################################### #

    def parse_id(self, content, *args, **kwargs):

        self.add_link(self.get_api(content), *args, **kwargs)
        return self.get_id(content)

    def parse_ids(self, content, *args, **kwargs):

        return [self.parse_id(value, *args, **kwargs) for value in content]

    # ####################################################### #

    def parse_name(self, content, *args, **kwargs):

        self.add_link(self.get_api(content), *args, **kwargs)
        return self.get_name(content)

    def parse_names(self, content, *args, **kwargs):

        return [self.parse_name(value, *args, **kwargs) for value in content]

    # ####################################################### #

    def parse_html(self, content, *args, res='', **kwargs):
        if isinstance(content, dict):
            if 'children' in content:
                if 'tag' in content:
                    res += '<' + content['tag'] + '>'
                    res = self.parse_html(content['children'], *args, res=res, **kwargs)
                    res += '</' + content['tag'] + '>'
                    if content['tag'] == 'a':
                        if 'data' in content:
                            self.add_link(self.get_api(content['data']), *args, priority=0, **kwargs)
                        if 'attributes' in content:
                            self.add_link(self.get_href(content['attributes']), *args, priority=-1, **kwargs)
                else:
                    res = self.parse_html(content['children'], *args, res=res, **kwargs)
            elif 'tag' in content:
                res += '<' + content['tag'] + '/>'
        if isinstance(content, list):
            for value in content:
                res = self.parse_html(value, *args, res=res, **kwargs)
        if isinstance(content, str):
            res += content
        return res

    def parse_htmls(self, content, *args, **kwargs):

        res = []
        for value in content:
            res.append(self.parse_html(value['body']['dom'].get('children', []), *args, **kwargs))
        return res

    # ####################################################### #

    def parse_artist_songs(self, content, *args, linker=True, id_artist='', **kwargs):

        ids = self.parse_ids([x['primary_artist'] for x in content], *args, linker=linker, **kwargs)
        names = self.parse_names([x['primary_artist'] for x in content], *args, linker=False, **kwargs)
        songs = []
        for _x, _id, _name in zip(content, ids, names):
            if _id == id_artist:
                songs.append(self.parse_id(_x, *args, linker=linker, cb_kwargs={'artist': _name}, **kwargs))
        return songs

    def parse_artists(self, content, *args, **kwargs):

        res = {}
        for value in content:
            res[value['label']] = self.parse_ids(value['artists'], *args, **kwargs)
        return res

    # ####################################################### #

    def parse_song_relations(self, content, *args, **kwargs):

        res = {}
        for value in content:
            res[value['type']] = self.parse_ids(value['songs'], *args, **kwargs)
        return res

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
