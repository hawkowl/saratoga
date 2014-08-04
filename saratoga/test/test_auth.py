from saratoga import auth
from saratoga import AuthenticationFailed


from twisted.web import server
from twisted.web.http_headers import Headers
from twisted.web.test.test_web import DummyChannel

from twisted.trial import unittest

from StringIO import StringIO


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

        host = "example.com"
        port = 8080
        body = "hi!"
        args = {}

        request = server.Request(DummyChannel(), False)
        request.gotLength(len(body))
        request.content = StringIO()
        request.content.write(body)
        request.content.seek(0)
        request.args = args
        request.setHost(host, port, False)
        request.uri = "example.com/test"
        request.path = "/test"
        request.method = "GET"
        request.clientproto = 'HTTP/1.1'

        import httpsig

        key_id = "alice"
        secret = "wonderland"
        
        hs = httpsig.HeaderSigner(key_id, secret, algorithm="hmac-sha256")
        signed_headers_dict = hs.sign({"Date": "Tue, 01 Jan 2014 01:01:01 GMT", "Host": "example.com"}, method="GET", path="/test")
        
        request.requestHeaders = Headers({x:[y] for x, y in signed_headers_dict.iteritems()})
        
        authDeferred = authenticator.auth_HMAC("alice", request)

        return authDeferred

