from twisted.trial.unittest import TestCase

from saratoga.api import SaratogaAPI
from saratoga import auth

import json

from base64 import b64encode as b64

class APIImpl(object):
    class v1(object):
        def requiresAuth_GET(self, request, params):
            return params["auth"]


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

        return self.api.test("/v1/requiresAuth", headers={
            "Authorization": ["BASIC {}".format(b64("bob:word"))]
            }).addCallback(rendered)


    def test_malformedAuthHeader(self):
        """
        Test that something that a malformed auth header is handled gracefully.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "fail", "data": "Malformed Authorization header."}
            )

        return self.api.test("/v1/requiresAuth", headers={
            "Authorization": ["BASIC HITHERE"]
            }).addCallback(rendered)


    def test_weirdAuthorizationHeader(self):
        """
        Test that weird auth headers are handled gracefully.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "fail", "data": "Malformed Authorization header."}
            )

        return self.api.test("/v1/requiresAuth", headers={
            "Authorization": ["BASIC {}".format(b64("bob:pass:word"))]
            }).addCallback(rendered)


    def test_unsupportedAuthType(self):
        """
        Test that a malformed auth header is handled gracefully.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "fail", "data": "Unsupported Authorization type "
                "'OMGLOLAUTH'"}
            )

        return self.api.test("/v1/requiresAuth", headers={
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

        return self.api.test("/v1/requiresAuth").addCallback(rendered)


    def test_correctBasicAuth(self):
        """
        Test that authentication works.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {"username": "bob@bob.com"}}
            )

        return self.api.test("/v1/requiresAuth", headers={
            "Authorization": ["BASIC {}".format(b64("bob:pass"))]
            }).addCallback(rendered)


    def test_correctHMACAuth(self):
        """
        Test that HMAC authentication works.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "success", "data": {"username": "bob@bob.com"}}
            )

        return self.api.test("/v1/requiresAuth", params={}, headers={
            "Authorization": ["HMAC-SHA256 {}".format(b64("bob:2c3df4dc5c5fd4d1c21b117d3b07c7a330e89ddf1b30e23ff0e7171e6394a2cc"))]
            }).addCallback(rendered)


    def test_wrongHMACAuth(self):
        """
        Test that wrong HMACs are rejected.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "fail", "data": "Authentication failed."}
            )

        return self.api.test("/v1/requiresAuth", params={"hi": "there"}, headers={
            "Authorization": ["HMAC-SHA256 {}".format(b64("bob:7785867505a1295459e71c53ab94ca6818de33668365432b7aca808ce02"
                "3a28b"))]
            }).addCallback(rendered)


    def test_unsupportedHMACAuth(self):
        """
        Test that trying to use an unsupported HMAC type is handled gracefully.
        """
        def rendered(request):
            self.assertEqual(
                json.loads(request.getWrittenData()),
                {"status": "fail", "data": "Unsupported HMAC type "
                "'MD5'"}
            )

        return self.api.test("/v1/requiresAuth", {}, headers={
            "Authorization": ["HMAC-MD5 {}".format(b64("bob:7785867505a1295459e71c53ab94ca6818de33668365432b7aca808ce02"
                "3a28b"))]
            }).addCallback(rendered)
