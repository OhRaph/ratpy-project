""" Ratpy URL module """

import re

# ############################################################### #
# ############################################################### #


class URL(str):

    """ Ratpy URL class """

    # ####################################################### #
    # ####################################################### #

    _domain = None
    _path = None
    _params = None
    _remaining = None

    # ####################################################### #

    def __new__(cls, url, remaining=None, **kwargs):

        _domain = URL.extract_domain(url)
        _path = URL.extract_path(url)
        _params = URL.extract_params(url)
        _remaining = remaining if remaining is not None else URL.extract_remaining(url)

        _params.update(kwargs)

        self = str.__new__(cls, URL._url(_path, _params))
        self._domain = _domain
        self._path = _path
        self._params = _params
        self._remaining = _remaining
        return self

    def __call__(self):
        return URL(URL._url(self.path, self._params))

    # ####################################################### #

    @property
    def infos(self):
        return {'path': self.path, 'params': self.params}

    # ####################################################### #
    # ####################################################### #

    @staticmethod
    def _url(path, params):
        res = path
        if params != {}:
            res += '?'
            res += '&'.join([k + ('=' + v if v else '') for (k, v) in params.items()])
        return res

    @staticmethod
    def _remove_protocol(path):
        search = re.search('[a-zA-Z]+://', path)
        return path[search.end():] if search else path

    # #######################################################

    @staticmethod
    def extract_domain(url):
        return URL._remove_protocol(url or '').split('/', 1)[0]

    @property
    def domain(self):
        return self._domain

    # ####################################################### #
    # ####################################################### #

    @staticmethod
    def extract_path(url):
        return (url or '').split('?', 1)[0].rstrip('/')

    @property
    def path(self):
        return self._path

    # ####################################################### #

    @staticmethod
    def extract_params(url):
        tmp = (url or '').split('?', 1)
        tmp = tmp[1].split('#', 1)[0] if len(tmp) > 1 else ''
        res = {}
        for param in map(lambda x: x.split('='), tmp.split('&')):
            if param[0] != '':
                res[param[0]] = param[1] if len(param) > 1 else None
        return res

    @property
    def params(self):
        return self._params

    # ####################################################### #
    # ####################################################### #

    @staticmethod
    def extract_remaining(url):
        return URL._remove_protocol(URL.extract_path(url))

    @property
    def remaining(self):
        return self._remaining

    # ####################################################### #
    # ####################################################### #

    def match(self, regex):
        if regex:
            if len(self.remaining) > 0 and isinstance(regex, str):
                return bool(re.search(re.compile('^'+regex), self.remaining))
            return False
        else:
            return True

    def next(self, regex):
        if regex:
            if len(self.remaining) > 0 and isinstance(regex, str):
                search = re.search(re.compile('^'+regex), self.remaining)
                return URL(self, remaining=self.remaining[search.end():] if search else '')
        else:
            return self

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
