from twisted.internet.defer import maybeDeferred, Deferred
from twisted.python import log, filepath
from twisted.python.failure import Failure
from twisted.web.resource import Resource
import twisted

from saratoga.test.requestMock import _testItem as testItem
from saratoga import (
    BadRequestParams,
    BadResponseParams,
    AuthenticationFailed,
    AuthenticationRequired,
    DoesNotExist,
    NoSuchEndpoint,
    APIError,
    outputFormats,
    __version__
)

from base64 import b64decode
from jsonschema import Draft4Validator

import re
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
        """
        Render a response to this Saratoga server.
        """
        # Some vars we'll need later
        args, api, version, processor = ({}, None, None, {})
        method = request.method.upper()

        # Figure out what output format we're going to be using
        outputFormat = self.api.outputRegistry.getFormat(request)

        if not outputFormat:
            # If there's no output format, return 406 Not Acceptable, as they
            # have asked for something we can't give them
            request.setResponseCode(406)
            request.write("406 Not Acceptable, please use one of: ")
            request.write(", ".join(self.api.outputRegistry._outputFormatsPreference))
            request.finish()
            return 1

        # Set the content type according to what was given before
        request.setHeader("Content-Type", outputFormat + "; charset=utf-8")
        # Say who we are!
        request.setHeader("Server", "Saratoga {} on Twisted {}".format(
                __version__, twisted.__version__))

        def _write(result):
            """
            Serialise and write a successful result.
            """
            if result is None:
                result = {}

            schema = processor.get("responseSchema")

            if schema:
                v = Draft4Validator(schema)
                errors = sorted(v.iter_errors(result), key=lambda e: e.path)

                if errors:
                    raise BadResponseParams(
                        ", ".join(e.message for e in errors))

            finishedResult = self.api.outputRegistry.renderAutomaticResponse(
                request, "success", result)

            request.write(finishedResult)
            request.finish()


        def _error(failure):
            """
            Something's gone wrong, write out an error.
            """
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
            elif isinstance(error, NoSuchEndpoint):
                errstatus = "error"
                errmessage = error.message
            else:
                errstatus = "fail"
                errmessage = error.message

            finishedResult = self.api.outputRegistry.renderAutomaticResponse(
                request, errstatus, errmessage)

            request.write(finishedResult)
            request.finish()


        def _runAPICall(authParams):
            """
            Run the function that we've looked up.
            """
            userParams["auth"] = authParams
            return maybeDeferred(func, self.api.serviceClass, request,
                                 userParams, *args)

        def _quickfail(fail):
            _error(Failure(fail))
            return 1

        endpointMethods = self.api.endpoints.get(method)

        if not endpointMethods:
            fail = BadRequestParams("Method not allowed.")
            fail.code = 405
            return _quickfail(fail)


        # Try and look up the static route in the endpoints list
        pathLookup = endpointMethods.get(tuple(request.postpath))

        if not pathLookup:
            # If there's no static route, try dynamic Django-style routes
            for item in endpointMethods:
                a = re.compile("^%s/%s$" % item)
                match = a.match("/".join(request.postpath))
                if match:
                    # We found it, so break out of here
                    pathLookup = endpointMethods[item]
                    args = match.groups()
                    break

        if not pathLookup:
            fail = NoSuchEndpoint("Endpoint does not exist.")
            return _quickfail(fail)
        else:
            # Some variables we'll need later
            params = {}

            # Expand out the looked up path
            api, version, processor = pathLookup

            # Read in the content from the request
            requestContent = request.content.read()
            # Set it back to the start
            request.content.seek(0)

            try:
                # Parse it from JSON
                # XXX: We should do this according to what it is, but JSON will
                # do for now
                params = json.loads(requestContent)
            except ValueError:
                pass

            # If there's no content body, but there are query args, put them in
            # a dictionary for us
            if not params and request.args is not None:
                for key, val in request.args.iteritems():
                    if type(val) in [list, tuple] and len(val) == 1:
                        params[key] = val[0]
                    else:
                        params[key] = val

            # Make sure it's a dict, even if it's empty
            params = {} if not params else params

            userParams = {"params": params}
            schema = processor.get("requestSchema")

            if schema:
                # Validate the schema, if we've got it
                v = Draft4Validator(schema)
                errors = sorted(v.iter_errors(params), key=lambda e: e.path)

                if errors:
                    return _quickfail(BadRequestParams(", ".join(
                        e.message for e in errors)))

            # Get the name of the endpoint
            funcname = api.get("func") or api["endpoint"]
            # Find the version class in the implementation
            versionClass = getattr(self.api.implementation, "v{}".format(version))
            # Do the dispatch, based on endpoint_method
            func = getattr(versionClass, "{}_{}".format(funcname, method)).im_func

            d = Deferred()

            #############################
            # Check for authentication. #
            #############################

            if api.get("requiresAuthentication", False):

                if not hasattr(self.api.serviceClass, "auth"):
                    fail = APIError("Authentication required, but there is not"
                        " an available authenticator.")
                    return _quickfail(fail)

                def _authAdditional(canonicalUsername):
                    return {"username": canonicalUsername}

                auth = request.getHeader("Authorization")

                if not auth:
                    fail = AuthenticationRequired("Authentication required.")
                    return _quickfail(fail)

                # Find out how we're authenticating
                authType, authDetails = auth.split()
                authType = authType.lower()

                if not authType in ["basic"] and  not authType.startswith("signature"):
                    fail = AuthenticationFailed(
                            "Unsupported Authorization type '{}'".format(
                                authType.upper()))
                    return _quickfail(fail)

                if authType == "basic":
                    try:
                        authDetails = b64decode(authDetails)
                        authUser, authPassword = authDetails.split(":")
                    except:
                        fail = AuthenticationFailed("Malformed Authorization header.")
                        return _quickfail(fail)

                    d.addCallback(lambda _:
                        self.api.serviceClass.auth.auth_usernameAndPassword(
                            authUser, authPassword))

                if authType.startswith("signature"):

                    keyBits = request.getHeader("Authorization")\
                                     .split("Signature ")[1].split(",")
                    keyBits = [z.split("=", 1) for z in keyBits]
                    keyBits = {x:y[1:-1] for x,y in keyBits}

                    d.addCallback(lambda _:
                            self.api.serviceClass.auth.auth_HMAC(keyBits["keyId"], request))

                d.addCallback(_authAdditional)

            d.addCallback(_runAPICall)
            d.addCallback(_write)
            d.addErrback(_error)

            # Kick off the chain
            d.callback(None)

            return 1


class SaratogaAPI(object):

    def __init__(self, implementation, definition, serviceClass=None, outputRegistry=None,
                 methods=["GET", "POST", "HEAD", "PUT", "DELETE", "PATCH"]):

        methods = [x.upper() for x in methods]

        if serviceClass:
            self.serviceClass = serviceClass
        else:
            self.serviceClass = DefaultServiceClass()

        if outputRegistry:
            self.outputRegistry = outputRegistry
        else:
            self.outputRegistry = outputFormats.OutputRegistry("application/json")
            self.outputRegistry.register("application/json",
                                         outputFormats.JSendJSONOutputFormat)
            self.outputRegistry.register("application/debuggablejson",
                                         outputFormats.DebuggableJSendJSONOutputFormat)

        # Where the implementation comes from
        self._implementation = implementation
        # Where we put the implementation in
        self.implementation = DefaultServiceClass()

        if not definition.get("metadata"):
            raise Exception("Definition requires a metadata section.")

        self.APIMetadata = definition["metadata"]
        self.APIDefinition = definition.get("endpoints", [])
        self._versions = self.APIMetadata["versions"]
        self.endpoints = {x:{} for x in methods}

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
            for verb in methods:
                for processor in api.get("{}Processors".format(
                        verb.lower()), []):

                    schemas = {
                        "requestSchema": processor.get("requestSchema"),
                        "responseSchema": processor.get("responseSchema")
                    }

                    for key, val in schemas.iteritems():
                        if isinstance(val, basestring):
                            i = json.load(filepath.FilePath(".").preauthChild(val).open())
                            processor[key] = i

                    for version in processor["versions"]:
                        if version not in self._versions:
                            raise Exception("Version mismatch - {} in {} is "
                                "not a declared version".format(
                                version, api["endpoint"]))

                        versionClass = getattr(
                            self.implementation, "v{}".format(version))
                        funcName = api.get("func") or api["endpoint"]
                        if not hasattr(versionClass,
                            "{}_{}".format(funcName, verb)):
                            raise Exception("Implementation is missing the {} "
                                "processor in the v{} {} endpoint".format(
                                    verb, version, funcName))

                        path = ('v' + str(version), api["endpoint"])
                        self.endpoints[verb][path] = (api, version, processor)


    def getResource(self):
        """
        Get the Twisted Web Resource.
        """
        return self.resource


    def test(self, path, params=None, headers=None, method="GET", useBody=True,
             replaceEmptyWithEmptyDict=False, enableHMAC=False):

        return testItem(self.resource, path, params=params, headers=headers,
            method=method, useBody=useBody, enableHMAC=enableHMAC,
            replaceEmptyWithEmptyDict=replaceEmptyWithEmptyDict)

    def run(self, port=8080): # pragma: no cover

        from twisted.web.server import Site
        from twisted.internet import reactor

        factory = Site(self.resource)
        reactor.listenTCP(port, factory)
        reactor.run()
