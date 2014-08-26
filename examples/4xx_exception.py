from saratoga.api import SaratogaAPI
from saratoga import BadRequestParams
import json

class ExampleAPI(object):
    class v1(object):
        def example_GET(self, request, params):
            raise BadRequestParams({"reason": "explosions!"})

SaratogaAPI(ExampleAPI, json.load(open("simple.json"))).run()
