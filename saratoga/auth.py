from saratoga import AuthenticationFailed
from twisted.internet import defer

import hashlib
import hmac



class InMemoryStringSharedSecretSource(object):

    def __init__(self, users):
        self.users = users


    def getUserDetails(self, username):

        for user in self.users:
            if user.get("username") == username:
                return defer.succeed(user)

        raise AuthenticationFailed("Authentication failed.")



class DummySharedSecretSource(object):

    def getUserDetails(self, username): # pragma: no cover
        raise AuthenticationFailed("Not a real authenticator.")



class DefaultAuthenticator(object):

    def __init__(self, sharedSecretSource):
        """
        Initialise the Haddock Authenticator.
        """
        self.sharedSecretSource = sharedSecretSource


    def _getUserDetails(self, username):

        if self.sharedSecretSource:
            d = self.sharedSecretSource.getUserDetails(username)
            return d

        raise AuthenticationFailed("No Authentication Backend")


    def auth_usernameAndPassword(self, username, password):

        def _continue(result):

            if result.get("username") == username and \
               result.get("password") == password:

                uName = result.get("canonicalUsername", result.get("Username"))
                return defer.succeed(uName)

            raise AuthenticationFailed("Authentication failed.")

        return self._getUserDetails(username).addCallback(_continue)


    def auth_HMAC(self, username, hmacUser, content, algorithm):

        def _continue(result):

            algo = getattr(hashlib, algorithm)

            hmacObj = hmac.new(result.get("password"), digestmod=algo)
            hmacObj.update(content)

            hmacResult = hmacObj.hexdigest()

            if hmacUser == hmacResult:
                uName = result.get("canonicalUsername", result.get("Username"))
                return defer.succeed(uName)

            raise AuthenticationFailed("Authentication failed.")

        return self._getUserDetails(username).addCallback(_continue)


