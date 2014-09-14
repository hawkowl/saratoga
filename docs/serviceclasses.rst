=======================================================
Introduction - Adding Global State with Service Classes
=======================================================

Most APIs are only useful with some form of global state - say, a database, or in-memory record of values.
Saratoga does this through **Service Classes** -- a separate class where you put all of your global state, without affecting any of your API implementation.


A Basic Service Class
=====================

Using the same ``planets.json`` as in the Introduction, modify ``planets.py`` to look like this:

.. code:: python

    import json
    from saratoga.api import SaratogaAPI, DefaultServiceClass

    class PlanetServiceClass(DefaultServiceClass):
        def __init__(self):
            self.yearLength = {
                "earth": {"seconds": 31536000},
                "pluto": {"seconds": 7816176000}
            }

    class PlanetAPI(object):
        class v1(object):
            def yearlength_GET(self, request, params):
                planetName = params["params"]["name"].lower()
                return self.yearLength.get(planetName)

    APIDescription = json.load(open("planets.json"))
    myAPI = SaratogaAPI(PlanetAPI, APIDescription, serviceClass=PlanetServiceClass())
    myAPI.run(port=8094)

So, let's have a look at what's different here - we now have a service class.

- We import ``DefaultServiceClass`` from ``saratoga.api`` and subclass it, adding things into it.
- We then pass in an instance (not a reference to the class, an instance) of our custom service class.
- In ``yearlength_GET``, we then access the ``yearLength`` dict defined in ``PlanetServiceClass``, using self.

The ``self`` of all of your processors is automatically set to your service class.
This means that you can do global state fairly easily, with the caveat that every version of your API accesses the same service class.
Saratoga won't be able to help you too much with global state differences, such as database schemas or the like, but you can isolate business logic changes in different API versions.

Accessing ``http://localhost:8094/v1/yearlength?name=earth`` in your web browser again will get the following back:

.. code:: json

    {
        "data": {
            "seconds": 31536000
	},
	"status": "success"
    }


Going Further
=============

Next, we'll have a look at Saratoga's parameter checking.
