from twisted.trial.unittest import TestCase
from twisted.python.modules import getModule

from shutil import copy

from saratoga.api import SaratogaAPI

import json

class APIImpl(object):
    class v1(object):
        def example_GET(self, request, params):
            return params["params"]

        def listResponse_GET(self, request, params):
            return params["params"]["data"]

        def exception_GET(self, request, params):
            raise Exception("OMG LOL WTF")

        def exampleregex_GET(self, request, params, someID):
            return {"id": someID}

        def __init__(self):
            self.jsonbodyParams_GET = self.example_GET
            self.urlParams_GET = self.example_GET
            self.requestParams_GET = self.example_GET
            self.responseParams_GET = self.example_GET
            self.responseParamsExtLoad_GET = self.example_GET
            self.dictResponse_GET = self.listResponse_GET
            self.requiresAuth_GET = self.example_GET
            self.invalidParamsType_GET = self.example_GET
            self.invalidResponseFormat_GET = self.example_GET


APIDef = {
    "metadata": {"versions": [1]},
    "endpoints": [
        {
            "endpoint": "example",
            "getProcessors": [{"versions": [1]}]
        },
        {
            "func": "exampleregex",
            "endpoint": r"example/(\d+)",
            "getProcessors": [{"versions": [1]}]
        },
        {
            "endpoint": "requestParams",
            "getProcessors": [{
                "versions": [1],
                "requestSchema": {
                    "properties": {
                        "hello": {},
                        "goodbye": {},
                        "the": {}
                    },
                    "additionalProperties": False,
                    "required": ["hello", "goodbye"]
                },
            }]
        },
        {
            "endpoint": "responseParamsExtLoad",
            "getProcessors": [{
                "versions": [1],
                "responseSchema": "jsonschemaext.json"
            }]
        },
        {
            "endpoint": "responseParams",
            "getProcessors": [{
                "versions": [1],
                "responseSchema": {
                    "properties": {
                        "cake": {},
                        "muffin": {},
                        "pizza": {}
                    },
                    "required": ["cake", "muffin"],
                    "additionalProperties": False
                }
            }]
        },
        {
            "endpoint": "listResponse",
            "getProcessors": [{"versions": [1], "responseSchema": {
                "type": "array"
            }}]
        },
        {
            "endpoint": "dictResponse",
            "getProcessors": [{"versions": [1], "responseSchema": {
                "type": "object"
            }}]
        },
        {
            "endpoint": "requiresAuth",
            "requiresAuthentication": True,
            "getProcessors": [{"versions": [1]}]
        },
        {
            "endpoint": "exception",
            "getProcessors": [{"versions": [1]}]
        },
        {
            "endpoint": "invalidParamsType",
            "getProcessors": [{"versions": [1], "paramsType":"bar"}]
        },
        {
            "endpoint": "invalidResponseFormat",
            "getProcessors": [{"versions": [1], "responseFormat":"bar"}]
        }
    ]
}

class SaratogaErrorCatchingTests(TestCase):
    """
    Testing when people do funny things to Saratoga.
    """
    def test_undeclaredVersion(self):
        APIDef = {
            "metadata": {"versions": [1]},
            "endpoints": [
                {
                    "endpoint": "example",
                    "getProcessors": [{"versions": [1, 2]}]
                }
            ]
        }

        try:
            SaratogaAPI(APIImpl, APIDef)
        except Exception, e:
            self.assertEqual(e.message,
                "Version mismatch - 2 in example is not a declared version")


    def test_missingVersionClass(self):
        APIDef = {
            "metadata": {"versions": [1,2]},
            "endpoints": [
                {
                    "endpoint": "example",
                    "getProcessors": [{"versions": [1, 2]}]
                }
            ]
        }

        try:
            SaratogaAPI(APIImpl, APIDef)
        except Exception, e:
            self.assertEqual(e.message,
                "Implementation is missing version 2")


    def test_missingMetadata(self):
        APIDef = {"endpoints": []}

        try:
            SaratogaAPI(APIImpl, APIDef)
        except Exception, e:
            self.assertEqual(e.message,
                "Definition requires a metadata section.")


    def test_missingImplementationInVersion(self):

        class APIImpl(object):
            class v1(object):
                def example_GET(self, request, params):
                    """"""
            class v2(object):
                """"""

        APIDef = {
            "metadata": {"versions": [1,2]},
            "endpoints": [
                {
                    "endpoint": "example",
                    "getProcessors": [{"versions": [1, 2]}]
                }
            ]
        }

        try:
            SaratogaAPI(APIImpl, APIDef)
        except Exception, e:
            self.assertEqual(e.message,
                "Implementation is missing the GET processor in the v2 example "
                "endpoint")



class SaratogaAPITests(TestCase):

    def setUp(self):
        fp = getModule(__name__).filePath
        copy(fp.parent().child("jsonschemaext.json").path, "jsonschemaext.json")
        
        self.api = SaratogaAPI(APIImpl, APIDef)

    def test_getResource(self):
        """
        Check that Saratoga returns the correct resource.
        """
        self.assertIs(self.api.resource, self.api.getResource())

    def test_basic(self):
        """
        Basic Saratoga test.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {}}
            )

        return self.api.test("/v1/example").addCallback(rendered)

    def test_basicWithEmptyParams(self):
        """
        Basic Saratoga test.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {}}
            )

        return self.api.test("/v1/example", replaceEmptyWithEmptyDict=True
            ).addCallback(rendered)

    def test_basicRegex(self):
        """
        Basic Saratoga test, testing the regex stuff.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {"id": "4"}}
            )

        return self.api.test("/v1/example/4").addCallback(rendered)
        
        
    def test_handlingOfExceptions(self):
        """
        Test that throwing a generic exception is handled gracefully.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "error", "data": "Internal server error."}
            )
            warnings = self.flushLoggedErrors()
            self.assertEqual(warnings[0].getErrorMessage(), "OMG LOL WTF")

        return self.api.test("/v1/exception").addCallback(rendered)


    def test_authRequiredWhenDefaultServiceClass(self):
        """
        Test that authentication without an authenticator fails.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "error", "data": "Internal server error."}
            )
            warnings = self.flushLoggedErrors()
            self.assertEqual(warnings[0].getErrorMessage(),
                "Authentication required, but there is not an available "
                "authenticator.")

        return self.api.test("/v1/requiresAuth").addCallback(rendered)


    def test_dictResponse(self):
        """
        Test that it allows a dict response.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {"hi": "there"}}
            )

        return self.api.test("/v1/dictResponse",
            params={"data": {"hi": "there"}}).addCallback(rendered)

    def test_dictResponsePOSTArgs(self):
        """
        Test that it allows a dict response.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {"hi": "there"}}
            )

        return self.api.test("/v1/dictResponse",
                             params={"data": {"hi": "there"}}, useBody=False).addCallback(rendered)


    def test_listResponse(self):
        """
        Test that it allows a list response.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": ["hi", "there"]}
            )

        return self.api.test("/v1/listResponse",
            params={"data": ["hi", "there"]}).addCallback(rendered)

    def test_listResponsePOSTArgs(self):
        """
        Test that it allows a list response.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": ["hi", "there"]}
            )

        return self.api.test("/v1/listResponse",
                             params={"data": [["hi", "there"]]}, useBody=False).addCallback(rendered)

    def test_dictResponseFailure(self):
        """
        Test that it handles responding with a non-dict gracefully when it is
        set to respond with a dict.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "error",
                "data": "Internal server error."}
            )
            warnings = self.flushLoggedErrors()
            self.assertEqual(warnings[0].getErrorMessage(),
                "[u'hi', u'there'] is not of type 'object'")

        d = self.api.test("/v1/dictResponse",
            params={"data": ["hi", "there"]})
        return d.addCallback(rendered)


    def test_listResponseFailure(self):
        """
        Test that it handles responding with a non-dict gracefully when it is
        set to respond with a dict.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "error",
                "data": "Internal server error."}
            )
            warnings = self.flushLoggedErrors()
            self.assertEqual(warnings[0].getErrorMessage(),
                "{u'hi': u'there'} is not of type 'array'")

        d = self.api.test("/v1/listResponse",
            params={"data": {"hi": "there"}})
        return d.addCallback(rendered)


    def test_serviceClass(self):
        """
        Test to make sure it uses the service class you tell it.
        """
        class Foo(object):
            pass

        serviceClass = Foo()
        api = SaratogaAPI(APIImpl, APIDef, serviceClass)
        self.assertEqual(api.serviceClass, serviceClass)


    def test_nonExistingEndpoint(self):
        """
        Test that it handles non-existing endpoints gracefully.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "error",
                "data": "Endpoint does not exist."}
            )
            warnings = self.flushLoggedErrors()
            self.assertEqual(warnings[0].getErrorMessage(),
                "Endpoint does not exist.")

        d = self.api.test("/v1/nowhere")
        return d.addCallback(rendered)


    def test_requiredResponseParamsAllowsOptionalParams(self):
        """
        Test that required response params work, and will return an error if
        given extras.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success",
                "data": {"cake": "yes", "muffin": "yes", "pizza": "slice"}}
            )

        d = self.api.test("/v1/responseParams",
            params={"cake": "yes", "muffin": "yes", "pizza": "slice"})
        return d.addCallback(rendered)


    def test_extLoadJSONSchema(self):
        """
        Test that it loads external JSON Schema by loading in something that it
        will fail.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "error",
                "data": "Internal server error."}
            )
            warnings = self.flushLoggedErrors()
            self.assertEqual(warnings[0].getErrorMessage(), "u'cake' is a "
                "required property, u'muffin' is a required property")
            
        return self.api.test("/v1/responseParamsExtLoad").addCallback(rendered)


    def test_requiredResponseParamsReturnsErrorIfNotGiven(self):
        """
        Test that required response params work, and will return an error if
        not given.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "error",
                "data": "Internal server error."}
            )
            warnings = self.flushLoggedErrors()
            self.assertEqual(warnings[0].getErrorMessage(), "'cake' is a "
                "required property, 'muffin' is a required property")

        return self.api.test("/v1/responseParams").addCallback(rendered)


    def test_requiredParamsReturnsErrorIfNotGiven(self):
        """
        Test that required params work, and will return an error if not given.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "fail",
                "data": "'hello' is a required property, 'goodbye' is a "
                    "required property"}
            )

        d = self.api.test("/v1/requestParams")
        return d.addCallback(rendered)


    def test_requiredParamsReturnsErrorIfGivenExtra(self):
        """
        Test that if required params are set, it will disallow unspecified
        params.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "fail",
                "data": "Additional properties are not allowed (u'unspecified'"
                    " was unexpected)"}
            )

        d = self.api.test("/v1/requestParams", params={
            "hello": "yes", "goodbye": "no", "unspecified": "yes"
            })
        return d.addCallback(rendered)


    def test_requiredParamsAllowsOptionalParams(self):
        """
        Test that if required params are set, it will allow params set as
        optional.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success",
                "data": {"hello": "yes", "goodbye": "no", "the": "beatles"}}
            )

        d = self.api.test("/v1/requestParams", params={
            "hello": "yes", "goodbye": "no", "the": "beatles"
            })
        return d.addCallback(rendered)
