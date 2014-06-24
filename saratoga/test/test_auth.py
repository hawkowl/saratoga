from saratoga import auth
from saratoga import AuthenticationFailed

from twisted.trial import unittest


class AuthTests(unittest.TestCase):

    def test_checkForNoAuthBackend(self):

        authenticator = auth.DefaultAuthenticator(None)

        f = authenticator.auth_usernameAndPassword("user", "pass")
        self.assertIsInstance(self.failureResultOf(f).value, AuthenticationFailed)


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


    def test_inMemoryStringSharedSecretSourceHMAC(self):

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

        authDeferred = authenticator.auth_HMAC("bob", "a878291f4cd5efdc03cdcc2e208b0174c29176624660e0338d6c7b88c3b05bcb", "hi", "sha256")

        return authDeferred

