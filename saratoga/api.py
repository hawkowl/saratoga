from twisted.web.resource import Resource


class DefaultServiceClass(object):
    """
    Placeholder.
    """

class SaratogaResource(Resource):
    isLeaf = True

    def __init__(self, api):

        self.api = api

    def render_GET(self, request):

        return request.path


class API(object):

    def __init__(self, implementation, definition, serviceClass=None):

        if serviceClass:
            pass
        else:
            self.serviceClass = DefaultServiceClass()

        self.inputImpl = implementation
        self.definition = definition

        self.resource = SaratogaResource(self)

        

    def getResource(self):

        return self.resource