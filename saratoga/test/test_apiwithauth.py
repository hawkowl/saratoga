from twisted.trial.unittest import TestCase

from saratoga.test.requestMock import testItem
from saratoga.api import SaratogaAPI
from saratoga import auth

import json

from base64 import b64encode as b64

class APIImpl(object):
    class v1(object):
        def requiresAuth_GET(self, request, params):
            return params


APIDef = {
    "metadata": {"versions": [1]},
    "endpoints": [
        {
            "endpoint": "requiresAuth",
            "requiresAuthentication": True,
            "getProcessors": [{"versions": [1]}]
        }
    ]
}

class APIServiceClass(object):

    def __init__(self):

        users = [
            {
                "username": "bob",
                "password": "pass",
                "canonicalUsername": "bob@bob.com"
            },
            {
                "username": "alice",
                "password": "word"
            }
        ]

        secretSource = auth.InMemoryStringSharedSecretSource(users)
        self.auth = auth.DefaultAuthenticator(secretSource)


class SaratogaAPITestsWithAuthenticator(TestCase):

    def setUp(self):
        self.api = SaratogaAPI(APIImpl, APIDef, APIServiceClass())

    def test_wrongPasswordBasicAuth(self):
        """
        Test that a wrong password with BASIC auth is handled gracefully.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "fail", "data": "Authentication failed."}
            )

        return testItem(self.api, "/v1/requiresAuth", headers={
            "Authorization": ["BASIC {}".format(b64("bob:word"))]
            }).addCallback(rendered)


    def test_unsupportedAuthType(self):
        """
        Test that something that Saratoga doesn't support is handled gracefully.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "fail", "data": "Unsupported Authorization type "
                "'OMGLOLAUTH'"}
            )

        return testItem(self.api, "/v1/requiresAuth", headers={
            "Authorization": ["OMGLOLAUTH FIODGNDSEGOUER"]
            }).addCallback(rendered)


    def test_noAuthTypeGiven(self):
        """
        Test that something that Saratoga doesn't support is handled gracefully.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "fail", "data": "Authentication required."}
            )

        return testItem(self.api, "/v1/requiresAuth").addCallback(rendered)


    def test_correctBasicAuth(self):
        """
        Test that authentication works.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {"saratoga_user": "bob@bob.com"}}
            )

        return testItem(self.api, "/v1/requiresAuth", headers={
            "Authorization": ["BASIC {}".format(b64("bob:pass"))]
            }).addCallback(rendered)






