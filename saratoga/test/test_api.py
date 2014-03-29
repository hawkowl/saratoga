from twisted.trial.unittest import TestCase

from saratoga.test.requestMock import testItem
from saratoga.api import SaratogaAPI

class APIImpl(object):
    class v1(object):
        def example_GET(self, request, params):
            return params

APIDef = {
    "metadata": {"versions": [1]},
    "endpoints": [
        {
            "endpoint": "example",
            "getProcessors": [{"versions": [1]}]
        }
    ]
}

class SaratogaAPITests(TestCase):

    def test_basic(self):

        def _cb(result):

            print result

        api = SaratogaAPI(APIImpl, APIDef).getResource()

        d = testItem(api, "/v1/example")
        d.addCallback(_cb)
        return d

                

