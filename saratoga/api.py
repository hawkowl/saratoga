from twisted.web.resource import Resource
from twisted.internet.defer import maybeDeferred

from saratoga import BadRequestParams, BadResponseParams, AuthenticationRequired


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

            result = _verifyReturnParams(result, processor)

            response = {
                "status": "success",
                "data": result
            }

            finishedResult = json.dumps(response)

            request.write(finishedResult)
            request.finish()



        api, version, processor = self.api.endpoints[request.method].get(
            request.path)

        if processor:

            request.setHeader("Content-Type", "application/json; charset=utf-8")


            versionClass = getattr(self.api.implementation, "v{}".format(version))

            func = getattr(versionClass, "{}_{}".format(api["endpoint"], request.method)).im_func

            params = {}

            d = maybeDeferred(func, self.api.serviceClass, request, params)
            d.addCallback(_write, request, api, processor)

            return 1

def _verifyReturnParams(result, APIInfo):

    returnFormat = APIInfo.get("returnFormat", "dict")

    if returnFormat == "dict":
        if not isinstance(result, dict):
            raise BadResponseParams("Result did not match the return format.")

        _checkReturnParamsDict(result, APIInfo)

    elif returnFormat == "list":
        if isinstance(result, basestring):
            items = json.loads(result)
        else:
            items = result

        if not isinstance(items, list):
            raise BadResponseParams("Result did not match the return format.")

        for item in items:
            _checkReturnParamsDict(item, APIInfo)

    return result

def _normaliseParams(params):

    finishedParams = []
    paramKeys = []

    for param in params:
        if isinstance(param, dict):
            options = []
            if param.get("paramOptions", None):
                for option in param.get("paramOptions", None):
                    if isinstance(option, dict):
                        options.append(option["data"])
                    elif isinstance(option, basestring):
                        options.append(option)

            paramKeys.append(param["param"])
            finishedParams.append({
                "param": param["param"],
                "paramOptions": options
            })
        elif isinstance(param, basestring):
            paramKeys.append(param)
            finishedParams.append({
                "param": param,
            })

    return (finishedParams, set(paramKeys))

def _checkParamOptions(item, data, exp):

    paramOptions = item.get("paramOptions", None)

    if paramOptions and not data in paramOptions:
        raise exp(
            "'%s' isn't part of %s in %s" % (data, json.dumps(paramOptions),
            item["param"]))

def _checkReturnParamsDict(result, processor):

    if result:
        keys = set(result.keys())
    else:
        keys = set()

    requiredInput = processor.get("requiredReturnParams", set())
    optionalInput = processor.get("optionalReturnParams", set())

    if not requiredInput or optionalInput:
        return True

    required, requiredKeys = _normaliseParams(requiredInput)
    optional, optionalKeys = _normaliseParams(optionalInput)
    accountedFor = set()

    for key, data in result.iteritems():
        for req in required + optional:
            if req["param"] == key:
                _checkParamOptions(req, data, BadResponseParams)
                accountedFor.add(req["param"])

    missing = requiredKeys - accountedFor
    extra = keys - (requiredKeys | optionalKeys)

    if missing:
        raise BadResponseParams("Missing response parameters: '%s'" % (
            "', '".join(sorted(missing))))
    if extra:
        raise BadResponseParams("Unexpected response parameters: '%s'" % (
            "', '".join(sorted(extra))))

    return True




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