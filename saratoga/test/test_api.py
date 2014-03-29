from twisted.trial.unittest import TestCase

from saratoga.test.requestMock import testItem
from saratoga.api import SaratogaAPI

import json

class APIImpl(object):
    class v1(object):
        def example_GET(self, request, params):
            return params

        def listResponse_GET(self, request, params):
            return params["data"]

        def __init__(self):
            self.jsonbodyParams_GET = self.example_GET
            self.urlParams_GET = self.example_GET
            self.requestParams_GET = self.example_GET
            self.responseParams_GET = self.example_GET
            self.dictResponse_GET = self.listResponse_GET
            self.listofdictResponse_GET = self.listResponse_GET
            self.paramOptions_GET = self.example_GET


APIDef = {
    "metadata": {"versions": [1]},
    "endpoints": [
        {
            "endpoint": "example",
            "getProcessors": [{"versions": [1]}]
        },
        {
            "endpoint": "jsonbodyParams",
            "getProcessors": [{"versions": [1]}]
        },
        {
            "endpoint": "urlParams",
            "getProcessors": [{"versions": [1], "paramsType": "url"}]
        },
        {
            "endpoint": "requestParams",
            "getProcessors": [{
                "versions": [1],
                "requiredParams": ["hello", "goodbye"],
                "optionalParams": ["the"]
            }]
        },
        {
            "endpoint": "responseParams",
            "getProcessors": [{
                "versions": [1],
                "requiredResponseParams": ["cake", "muffin"],
                "optionalResponseParams": ["pizza"]
            }]
        },
        {
            "endpoint": "listResponse",
            "getProcessors": [{"versions": [1], "responseFormat": "list"}]
        },
        {
            "endpoint": "listofdictResponse",
            "getProcessors": [{"versions": [1], "responseFormat": "listofdict"}]
        },
        {
            "endpoint": "dictResponse",
            "getProcessors": [{"versions": [1], "responseFormat": "dict"}]
        },
        {
            "endpoint": "paramOptions",
            "getProcessors": [{"versions": [1], "requiredParams": [
            {"param": "foo", "paramOptions": ["bar", {"data": "baz"}]}]}]
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
                    return params
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
        self.api = SaratogaAPI(APIImpl, APIDef)


    def test_basic(self):
        """
        Basic Saratoga test.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {}}
            )

        return testItem(self.api, "/v1/example").addCallback(rendered)


    def test_paramOptions(self):
        """
        Test that param options work.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {"foo": "bar"}}
            )

        return testItem(self.api, "/v1/paramOptions", params={
            "foo": "bar"
            }).addCallback(rendered)


    def test_paramOptionsFailure(self):
        """
        Test that it handles paramOptions failing gracefully.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "fail",
                "data": "'cake' isn't part of [\"bar\", \"baz\"] in foo"}
            )

        return testItem(self.api, "/v1/paramOptions",
            params={"foo": "cake"}).addCallback(rendered)


    def test_dictResponse(self):
        """
        Test that it allows a dict response.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {"hi": "there"}}
            )

        return testItem(self.api, "/v1/dictResponse", params={
            "data": {"hi": "there"}
            }).addCallback(rendered)


    def test_listResponse(self):
        """
        Test that it allows a list response.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": ["hi", "there"]}
            )

        return testItem(self.api, "/v1/listResponse",
            params={"data": ["hi", "there"]}).addCallback(rendered)


    def test_listofdictResponse(self):
        """
        Test that it allows a list of dict response.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": [{"hi": "there"}]}
            )

        return testItem(self.api, "/v1/listofdictResponse",
            params={"data": [{"hi": "there"}]}).addCallback(rendered)


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
                "Result did not match the response format.")

        d = testItem(self.api, "/v1/dictResponse",
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
                "Result did not match the response format.")

        d = testItem(self.api, "/v1/listResponse",
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

        d = testItem(self.api, "/v1/nowhere")
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

        d = testItem(self.api, "/v1/responseParams",
            params={"cake": "yes", "muffin": "yes", "pizza": "slice"})
        return d.addCallback(rendered)


    def test_requiredResponseParamsReturnsErrorIfGivenExtra(self):
        """
        Test that required response params work, and will return an error if
        given extras.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "error",
                "data": "Internal server error."}
            )
            warnings = self.flushLoggedErrors()
            self.assertEqual(warnings[0].getErrorMessage(),
                "Unexpected response parameters: 'foo'")

        d = testItem(self.api, "/v1/responseParams",
            params={"cake": "yes", "muffin": "yes", "foo": "bar"})
        return d.addCallback(rendered)


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
            self.assertEqual(warnings[0].getErrorMessage(),
                "Missing response parameters: 'cake', 'muffin'")

        d = testItem(self.api, "/v1/responseParams")
        return d.addCallback(rendered)


    def test_requiredParamsReturnsErrorIfNotGiven(self):
        """
        Test that required params work, and will return an error if not given.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "fail",
                "data": "Missing request parameters: 'goodbye', 'hello'"}
            )

        d = testItem(self.api, "/v1/requestParams")
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
                "data": "Unexpected request parameters: 'unspecified'"}
            )

        d = testItem(self.api, "/v1/requestParams", params={
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

        d = testItem(self.api, "/v1/requestParams", params={
            "hello": "yes", "goodbye": "no", "the": "beatles"
            })
        return d.addCallback(rendered)


    def test_jsonbodyParams(self):
        """
        Test that params delivered through JSON work.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {"hello": "there"}}
            )

        d = testItem(self.api, "/v1/jsonbodyParams", params={"hello": "there"})
        return d.addCallback(rendered)


    def test_urlParams(self):
        """
        Test that params delivered through URL params work.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {"hello": "there"}}
            )

        d = testItem(self.api, "/v1/urlParams", params={"hello": "there"},
            useBody=False)
        return d.addCallback(rendered)
