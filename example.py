from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

from saratoga.api import SaratogaAPI, DefaultServiceClass

import json


class myServiceClass(DefaultServiceClass):
    def __init__(self):
        self.weather = {"temperature": 30, "windSpeed": 20, "isRaining": False}

    def doSomething(self):
        return self.weather


class APIExample(object):
    class v1(object):
        def weather_GET(self, request, params):
            return self.doSomething()

    class v2(object):
        def __init__(self, outer):
            pass

        def weather_GET(self, request, params):
            return {"temperature": 30, "windSpeed": 20, "isRaining": "YES"}


root = SaratogaAPI(APIExample, json.load(open("APIExample.json")), myServiceClass())
factory = Site(root.getResource())
reactor.listenTCP(8888, factory)
reactor.run()