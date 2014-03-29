from twisted.trial.unittest import TestCase

from saratoga.test.requestMock import testItem
from saratoga.api import SaratogaAPI

import json

class APIImpl(object):
    class v1(object):
        def example_GET(self, request, params):
            return params

        def __init__(self):
            self.jsonbodyParams_GET = self.example_GET
            self.urlParams_GET = self.example_GET
            self.requestParams_GET = self.example_GET
            self.responseParams_GET = self.example_GET

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
        }
    ]
}

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

