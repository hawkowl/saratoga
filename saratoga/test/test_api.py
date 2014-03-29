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


    def test_jsonbodyParams(self):
        """
        Test that params delivered through JSON work.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {"hello": "there"}}
            )

        d = testItem(self.api, "/v1/jsonbodyParams", params={"hello": "there"},
            useBody=True)
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

        d = testItem(self.api, "/v1/urlParams", params={"hello": "there"})
        return d.addCallback(rendered)

