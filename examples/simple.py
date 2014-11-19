from saratoga.api import SaratogaAPI
import json

class ServiceClassExample(object):
    stuff = "foo"

class ExampleAPI(object):
    class v1(object):
        def example_GET(self, request, params):
            return self.stuff

api = SaratogaAPI(ExampleAPI, json.load(open("simple.json")), serviceClass=ServiceClassExample())
api.run()
