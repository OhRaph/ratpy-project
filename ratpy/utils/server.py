""" Ratpy Test Server module """

import random

from urllib.parse import urlencode

from twisted.web.resource import Resource
from twisted.web.server import Site

# ############################################################### #
# ############################################################### #


class TestServer(Resource):

    """ Ratpy Test Server class """

    isLeaf = True

    def getChild(self, name, request):
        return self

    def render(self, request):

        def get_arg(name, default=None):
            return int(request.args.get(name, [default])[0])

        nb_pages = get_arg(b'nb_pages', 100)
        nb_page_links = get_arg(b'nb_page_links', 10)

        request.write(b"<html><head></head><body>")
        args = request.args.copy()

        for page in [random.randint(1, nb_pages) for _ in range(nb_page_links)]:
            args[b'page'] = page
            argstr = urlencode(args, doseq=True)
            request.write('<a href=\'?{}\'>Link to page {}</a><br>'.format(argstr, page).encode('utf8'))
        request.write(b"</body></html>")
        return b''

# ############################################################### #
# ############################################################### #


if __name__ == '__main__':

    """ Ratpy Test Server program """

    from twisted.internet import reactor

    root = TestServer()
    factory = Site(root)
    httpPort = reactor.listenTCP(8998, factory)

    def _print_listening():
        httpHost = httpPort.getHost()
        print("Server open at http://{}:{}".format(httpHost.host, httpHost.port))

    reactor.callWhenRunning(_print_listening)
    reactor.run()

# ############################################################### #
# ############################################################### #
