==============================
Introduction -- Authentication
==============================

.. note::

   This hasn't been adapted from Haddock yet, so is wrong in places (pretty much everywhere).

Some APIs may need authentication before accessing - for example, if you are writing a service rather than just a public data API. Haddock allows you to either do the authentication yourself, or hook in a "Shared Secret Source" which will request a user's shared secret from your backend.

Using a Shared Secret Source
============================

For this example, we will be using a new API Description.

API Description
---------------

Put this in ``authapi.json``::

    {
        "metadata": {
            "name": "authapi",
            "friendlyName": "An Authenticated API",
            "versions": [1],
            "apiInfo": true
        },
        "api": [
            {
                "name": "supersecretdata",
                "friendlyName": "Super secret data endpoint!!!!",
                "endpoint": "supersecretdata",
                "requiresAuthentication": true,
                "getProcessors": [
                    {
                        "versions": [1]
                    }
                ]
            }
        ]
    }

The new part of this is ``requiresAuthentication`` in our single API, which is now set to ``true``.

Python Implementation
---------------------

Put this into ``authapi.py``::

    import json
    from haddock.api import API, DefaultServiceClass
    from haddock import auth

    class AuthAPIServiceClass(DefaultServiceClass):
        def __init__(self):
            users = [{
                "username": "squirrel",
                "canonicalUsername": "secretsquirrel@mi6.gov.uk",
                "password": "secret"
            }]
            self.auth = auth.DefaultHaddockAuthenticator(
                auth.InMemoryStringSharedSecretSource(users))

    class AuthAPI(object):
        class v1(object):
            def supersecretdata_GET(self, request, params):
                return "Logged in as %s" % (params.get("haddockAuth"),)

    APIDescription = json.load(open("authapi.json"))
    myAPI = API(AuthAPI, APIDescription, serviceClass=AuthAPIServiceClass())
    myAPI.getApp().run("127.0.0.1", 8094)

In our implementation, we now import ``haddock.auth``, and use two portions of it when creating our service class. We set ``self.auth`` to be a new instance of ``auth.DefaultHaddockAuthenticator``, with a ``auth.InMemoryStringSharedSecretSource`` as its only argument, with that taking a list of users.

How Authentication in Haddock Works
-----------------------------------

Before your API method is called, Haddock checks the API description, looking for ``requiresAuthentication`` on the endpoint. If it's found, then it will look in the HTTP ``Authorized`` header for ``Basic``. It will then call ``auth_usernameAndPassword`` on the Haddock authenticator, which will then check it and decide whether or not to allow the request.

Since this is boilerplate, Haddock abstracts it into the ``DefaultHaddockAuthenticator``, which takes a ``SharedSecretSource``. Currently, the source requires only one function - ``getUserDetails``. This is called, asking for the details of a user, which the authenticator will then check against the request. If it is successful, the authenticator will return either the user's *canonical username* or their username.

Canonical usernames are returned by the Haddock authenticator when possible, which are then placed in a ``haddockAuth`` param. Your API method will get this, and know that this is the user which has been successfully authenticated.

The ``InMemoryStringSharedSecretSource`` Source
-----------------------------------------------

The ``InMemoryStringSharedSecretSource`` takes a list of users, which consists of a ``username``, ``password`` and optionally a ``canonicalUsername``.

Running It
----------

Now, since we have got our authentication-capable API, let's test it. Try running ``curl http://localhost:8094/v1/supersecretdata``, you should get this back::

    {"status": "fail", "data": "Authentication required."}

Haddock is now checking for authentication. Let's try giving it a username and password, with ``curl http://localhost:8094/v1/supersecretdata -u squirrel:secret``::

    {"status": "success", "data": "Logged in as secretsquirrel@mi6.gov.uk"}

As you can see, we returned the canonical username in ``supersecretdata_GET``, which is ``secretsquirrel@mi6.gov.uk``.


Why Canonical Usernames?
========================

Since this is an API, it may have sensitive data behind it, which you want to control access to. Controlling it via authentication is only solving part of the problem - you need to make sure that if the shared secret is lost, you can rescind access to it. Since changing passwords is a pain for users, a better solution is to have *API specific credentials*, and Haddock's authentication is made to support that.

When giving out access to an API, you should create a set of API specific credentials - that is, a randomly generated username and password which is then used against your API, and can be revoked if required. Simply store the random creds, and a link to the user's real (canonical) username, and give that to the authenticator.

Implementing Your Own Shared Secret Source
==========================================

This is taken from Tomato Salad, a project using Haddock.
::

    class tsSharedSecretSource(object):
        def __init__(self, db):
            self.db = db

        def getUserDetails(self, username):
            def _continue(result):
                if result:
                    res = {}
                    res["username"] = result["APIKeyUsername"]
                    res["canonicalUsername"] = result["userEmail"]
                    res["password"] = result["APIKeyPassword"]
                    return res
                raise AuthenticationFailed("Incorrect API key.")

            d = self.db.fetchAPIKey(username)
            d.addCallback(_continue)
            return d

    class tsServiceClass(DefaultServiceClass):
        def __init__(self):
            self.db = Database(
                {"connectionString": "sqlite:///tomatosalad.db"})
            self.auth = DefaultHaddockAuthenticator(
                tsSharedSecretSource(self.db))
