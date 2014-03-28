from twisted.web.resource import Resource
from twisted.internet.defer import maybeDeferred
from twisted.python.failure import Failure

from saratoga.tools import _verifyReturnParams, _getParams
from saratoga import (
    BadRequestParams,
    BadResponseParams,
    AuthenticationRequired,
    DoesNotExist
)


import json, saratoga, twisted, traceback, sys

class DefaultServiceClass(object):
    """
    Placeholder.
    """

class SaratogaResource(Resource):
    isLeaf = True

    def __init__(self, api):

        self.api = api

    def render(self, request):

        def _write(result, request, api, processor):

            result = _verifyReturnParams(result, processor)

            response = {
                "status": "success",
                "data": result
            }

            finishedResult = json.dumps(response)

            request.write(finishedResult)
            request.finish()
            

        def _error(failure, request, api, processor):
            
            error = failure.value
            errorcode = 500

            if not isinstance(error, BadRequestParams):
                traceback.print_exc(file=sys.stderr)
            if hasattr(error, "code"):
                errorcode = error.code

            request.setResponseCode(errorcode)

            if errorcode == 500:
                errstatus = "error"
                errmessage = "Internal server error."
            else:
                errstatus = "fail"
                errmessage = error.message

            response = {
                "status": errstatus,
                "data": errmessage
            }

            request.write(json.dumps(response))
            request.finish()

        request.setHeader("Content-Type", "application/json; charset=utf-8")
        request.setHeader("Server", "Saratoga {} on Twisted {}".format(
                saratoga.__version__, twisted.__version__))

        api, version, processor = self.api.endpoints[request.method].get(
            request.path, (None, None, None))

        if processor:

            versionClass = getattr(self.api.implementation, "v{}".format(version))
            func = getattr(versionClass, "{}_{}".format(api["endpoint"], request.method)).im_func

            # Getting parameters

            paramsType = processor.get("paramsType", "jsonbody")

            try:
                if paramsType == "url":
                    args = request.args
                    params = {}
                    for key, data in args.iteritems():
                        params[key] = data[0]
                    params = _getParams(params, processor)
                elif paramsType == "jsonbody":
                    requestContent = request.content.read()
                    params = json.loads(requestContent)
                    params = _getParams(params, processor)
            except Exception, e:
                _error(Failure(e), request, api, processor)
                return 1

            d = maybeDeferred(func, self.api.serviceClass, request, params)
            d.addCallback(_write, request, api, processor)
            d.addErrback(_error, request, api, processor)

        else:
            fail = DoesNotExist("Endpoint does not exist.")
            _error(Failure(fail), request, None, None)

        return 1



class SaratogaAPI(object):

    def __init__(self, implementation, definition, serviceClass=None):

        if serviceClass:
            self.serviceClass = serviceClass
        else:
            self.serviceClass = DefaultServiceClass()

        self._implementation = implementation
        self.implementation = DefaultServiceClass()

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

        for version in self._versions:
            try:
                i = getattr(self._implementation, "v{}".format(version))(self.serviceClass)
            except TypeError:
                i = getattr(self._implementation, "v{}".format(version))()

            setattr(self.implementation, "v{}".format(version), i)

        for api in self.APIDefinition:

            for verb in ["GET", "POST"]:
                for processor in api.get("{}Processors".format(verb.lower()), []):

                    for version in processor["versions"]:

                        if version not in self._versions:
                            raise Exception("Version mismatch - {} in {} is not a declared version".format(version, api["endpoint"]))

                        path = "/v{}/{}".format(version, api["endpoint"])

                        self.endpoints[verb][path] = (api, version, processor)






    def getResource(self):

        return self.resource