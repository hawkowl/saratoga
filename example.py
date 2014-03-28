from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

from saratoga.api import SaratogaAPI

import json

root = SaratogaAPI({}, json.load(open("APIExample.json")))
factory = Site(root.getResource())
reactor.listenTCP(8880, factory)
reactor.run()