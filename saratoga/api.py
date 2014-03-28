from twisted.web.resource import Resource

import json

class DefaultServiceClass(object):
    """
    Placeholder.
    """

class SaratogaResource(Resource):
    isLeaf = True

    def __init__(self, api):

        self.api = api

    def render(self, request):

        processor = self.api.endpoints[request.method].get(request.path)

        if processor:
            return json.dumps(processor)
        else:
            request.setResponseCode(404)
            return "NOPE"


class SaratogaAPI(object):

    def __init__(self, implementation, definition, serviceClass=None):

        if serviceClass:
            pass
        else:
            self.serviceClass = DefaultServiceClass()

        self.inputImpl = implementation

        if not definition.get("metadata"):
            raise Exception("Definition requires a metadata section.")

        self.APIMetadata = definition["metadata"]
        self.APIDefinition = definition.get("api", [])

        self.resource = SaratogaResource(self)

        self._versions = self.APIMetadata["versions"]

        self.endpoints = {
            "GET": {},
            "POST": {}
        }

        for api in self.APIDefinition:

            for verb in ["GET", "POST"]:
                for processor in api.get("{}Processors".format(verb.lower()), []):

                    for version in processor["versions"]:

                        if version not in self._versions:
                            raise Exception("Version mismatch - {} in {} is not a declared version".format(version, api["endpoint"]))

                        path = "/v{}/{}".format(version, api["endpoint"])

                        self.endpoints[verb][path] = processor






    def getResource(self):

        return self.resource