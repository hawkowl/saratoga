=======================================================
Introduction - Adding Global State with Service Classes
=======================================================

Most APIs are only useful with some form of global state - say, a database, or in-memory record of values. Haddock does this through **Service Classes** - a separate class where you put all of your global state, without affecting any of your API implementation.


A Basic Service Class
=====================

Using the same ``planets.json`` as in the Introduction, modify ``planets.py`` to look like this::

    import json
    from haddock.api import API, DefaultServiceClass

    class PlanetServiceClass(DefaultServiceClass):
        def __init__(self):
            self.yearLength = {
                "earth": {"seconds": 31536000},
                "pluto": {"seconds": 7816176000}
            }

    class PlanetAPI(object):
        class v1(object):
            def yearlength_GET(self, request, params):
                planetName = params["name"].lower()
                return self.yearLength.get(planetName)

    APIDescription = json.load(open("planets.json"))
    myAPI = API(PlanetAPI, APIDescription, serviceClass=PlanetServiceClass())
    myAPI.getApp().run("127.0.0.1", 8094)

So, let's have a look at what's different here - we now have a service class.

- We import ``DefaultServiceClass`` from ``haddock.api`` and subclass it, adding things into it.
- We then pass in an instance (not a reference to the class, an instance) of our custom service class.
- In ``yearlength_GET``, we then access the ``yearLength`` dict defined in ``PlanetServiceClass``, using self.

Additionally, the ``self`` of all of your processors is automatically set to your service class. This means that you can do global state fairly easily - but it does mean that every version of your API accesses the same service class. Haddock won't be able to help you too much with global state differences, such as database schemas or the like, but you can isolate business logic changes in different API versions.


Subclassing Is Optional
=======================

The subclassing is done to provide some boilerplate Klein routes which allow the automatic API documentation and CORS support to work. You can create your own blank service class, and everything except those two things will work perfectly. This is also test covered.


Going Further
=============

Next, we'll have a look at Haddock's parameter checking.