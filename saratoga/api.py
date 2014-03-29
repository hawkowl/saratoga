from twisted.web.resource import Resource
from twisted.internet.defer import maybeDeferred
from twisted.python.failure import Failure
from twisted.python import log
import twisted

from saratoga.tools import _verifyResponseParams, _getParams
from saratoga import (
    BadRequestParams,
    #BadResponseParams,
    #AuthenticationRequired,
    DoesNotExist,
    __gitversion__
)



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

        def _write(result, request, api, processor):

            res = _verifyResponseParams(result, processor)

            response = {
                "status": "success",
                "data": res
            }

            finishedResult = json.dumps(response)

            request.write(finishedResult)
            request.finish()
            

        def _error(failure, request, api, processor):
            
            error = failure.value
            errorcode = 500

            if not isinstance(error, BadRequestParams):
                log.err(failure)
            if hasattr(error, "code"):
                errorcode = error.code

            request.setResponseCode(errorcode)

            if errorcode == 500:
                errstatus = "error"
                errmessage = "Internal server error."
            elif errorcode == 404:
                errstatus = "error"
                errmessage = error.message
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
                __gitversion__, twisted.__version__))

        #print "Looking for {}".format(request.path)

        api, version, processor = self.api.endpoints[request.method].get(
            request.path, (None, None, None))

        if processor:

            versionClass = getattr(
                self.api.implementation, "v{}".format(version))
            func = getattr(versionClass, "{}_{}".format(
                api["endpoint"], request.method)).im_func

            ########################
            # Get some parameters. #
            ########################

            paramsType = processor.get("paramsType", "jsonbody")

            try:
                if paramsType == "url":
                    args = request.args
                    params = {}
                    for key, data in args.iteritems():
                        params[key] = data
                    params = _getParams(params, processor)
                elif paramsType == "jsonbody":
                    requestContent = request.content.read()
                    if requestContent:
                        params = json.loads(requestContent)
                    else:
                        params = {}
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
        self.APIDefinition = definition.get("endpoints", [])
        self._versions = self.APIMetadata["versions"]
        self.endpoints = {
            "GET": {},
            "POST": {}
        }

        self.resource = SaratogaResource(self)

        for version in self._versions:
            try:
                i = getattr(self._implementation, "v{}".format(version))(
                    self.serviceClass)
            except TypeError:
                i = getattr(self._implementation, "v{}".format(version))()
            except Exception:
                raise Exception(
                    "Implementation is missing version {}".format(version))

            setattr(self.implementation, "v{}".format(version), i)

        for api in self.APIDefinition:
            for verb in ["GET", "POST"]:
                for processor in api.get(
                    "{}Processors".format(verb.lower()), []):
                    for version in processor["versions"]:
                        if version not in self._versions:
                            raise Exception("Version mismatch - {} in {} is "
                                "not a declared version".format(
                                version, api["endpoint"]))

                        versionClass = getattr(
                            self.implementation, "v{}".format(version))
                        if not hasattr(versionClass,
                            "{}_{}".format(api["endpoint"], verb)):
                            raise Exception("Implementation is missing the {} " 
                                "processor in the v{} {} endpoint".format(
                                    verb, version, api["endpoint"]))

                        path = "/v{}/{}".format(version, api["endpoint"])
                        self.endpoints[verb][path] = (api, version, processor)


    def getResource(self):

        return self.resource

    def run(self, port=8080): # pragma: no cover

        from twisted.web.server import Site
        from twisted.internet import reactor

        factory = Site(self.resource)
        reactor.listenTCP(port, factory)
        reactor.run()
