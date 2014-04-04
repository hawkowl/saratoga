from saratoga import auth
from saratoga import AuthenticationFailed

from twisted.trial import unittest


class AuthTests(unittest.TestCase):

    def test_checkForNoAuthBackend(self):

        authenticator = auth.DefaultAuthenticator(None)

        self.assertRaises(
            AuthenticationFailed, authenticator.auth_usernameAndPassword,
            "user", "pass")


    def test_inMemoryStringSharedSecretSourcePassword(self):

        def _catch(res):
            self.assertIsInstance(res.value, AuthenticationFailed)

        users = [
            {
                "username": "bob",
                "password": "42"
            },
            {
                "username": "alice",
                "canonicalUsername": "alice@houseofcar.ds",
                "password": "wonderland"
            }
        ]

        authenticator = auth.DefaultAuthenticator(
            auth.InMemoryStringSharedSecretSource(users))

        authDeferred = authenticator.auth_usernameAndPassword(
            "alice", "wonderland")
        authDeferred.addCallback(self.assertEqual, "alice@houseofcar.ds")
        authDeferred.addCallback(
            lambda _: authenticator.auth_usernameAndPassword(
                "bob", "pass")).addErrback(_catch)
        authDeferred.addCallback(
            lambda _: authenticator.auth_usernameAndPassword(
                "peter", "pass")).addErrback(_catch)

        return authDeferred


    def test_inMemoryStringSharedSecretSourceHMACNotImplemented(self):

        def _catch(res):
            self.assertIsInstance(res.value, NotImplementedError)

        users = [
            {
                "username": "bob",
                "password": "42"
            },
            {
                "username": "alice",
                "password": "wonderland"
            }
        ]

        authenticator = auth.DefaultAuthenticator(
            auth.InMemoryStringSharedSecretSource(users))

        authDeferred = authenticator.auth_usernameAndHMAC(
            "alice", "this is not a hmac").addErrback(_catch)

        return authDeferred
