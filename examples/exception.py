from saratoga.api import SaratogaAPI
import json

class ExampleAPI(object):
    class v1(object):
        def example_GET(self, request, params):
            raise Exception("oh no!")

SaratogaAPI(ExampleAPI, json.load(open("simple.json"))).run()
