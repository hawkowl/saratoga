from saratoga.api import SaratogaAPI
import json

class APIExample(object):
    class v1(object):
        def example_GET(self, request, params):
            
            print self
            print request
            print params

            return params
            #return {"res": (self, request, params)}

api = SaratogaAPI(APIExample, json.load(open("example2.json")))
api.run(8888)