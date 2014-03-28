from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

from saratoga.api import API

root = API({}, {})
factory = Site(root.getResource())
reactor.listenTCP(8880, factory)
reactor.run()