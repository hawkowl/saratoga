=================================
Introduction - Parameter Checking
=================================

Haddock contains support for checking parameters given to your API. It supports checking for required and optional params, as well as restricting the content of each to certain values.


Required & Optional Params
==========================

This will show you how to use the required and optional params.

API Documentation
-----------------

Using the ``planets.json`` example from before, let's add a new API - this time, for getting the distance from the sun.
::

    {
        "metadata": {
            "name": "planetinfo",
            "friendlyName": "Planet Information",
            "versions": [1],
            "apiInfo": true
        },
        "api": [
            {
                "name": "sundistance",
                "friendlyName": "Distance from the Sun for Planets",
                "endpoint": "sundistance",
                "getProcessors": [
                    {
                        "versions": [1],
                        "requiredParams": ["name"],
                        "optionalParams": ["useImperial"],
                        "returnParams": ["distance"],
                        "optionalReturnParams": ["unit"]
                    }
                ]
            },
            {
                "name": "yearlength",
                "friendlyName": "Year Length of Planets",
                "endpoint": "yearlength",
                "getProcessors": [
                    {
                        "versions": [1],
                        "requiredParams": ["name"]
                    }
                ]
            }
        ]
    }

So now we've added a ``sundistance`` API, with a single processor. It has the following restrictions:

- For the request, ``name`` **must** be provided and ``useImperial`` **may** be.
- For the response, ``distance`` **must** be provided, and ``unit`` **may** be.

Python Implementation
---------------------

So, lets add the code to do this into ``planets.py``::

    import json
    from haddock.api import API, DefaultServiceClass

    class PlanetServiceClass(DefaultServiceClass):
        def __init__(self):
            self.yearLength = {
                "earth": {"seconds": 31536000},
                "pluto": {"seconds": 7816176000}
            }
            self.sunDistance = {
                "earth": {"smoots": 87906922100, "miles": 92960000},
                "pluto": {"smoots": 3470664162652, "miles": 3670050000}
            }

    class PlanetAPI(object):
        class v1(object):
            def yearlength_GET(self, request, params):
                planetName = params["name"].lower()
                return self.yearLength.get(planetName)

            def sundistance_GET(self, request, params):
                planetName = params["name"].lower()
                sunDistance = self.sunDistance.get(planetName)
                if sunDistance and params.get("useImperial"):
                    return {"distance": sunDistance["miles"]}
                else:
                    return {"distance": sunDistance["smoots"], "unit": "smoots"}

    APIDescription = json.load(open("planets.json"))
    myAPI = API(PlanetAPI, APIDescription, serviceClass=PlanetServiceClass())
    myAPI.getApp().run("127.0.0.1", 8094)

We now have an implementation that will return the *distance* if ``useImperial`` is some truthy value, and *distance* and *unit* otherwise. The API will not force you to specify ``useImperial`` as an API consumer, nor ``unit`` as a developer. Please note that not being specified will make it not appear in the dict, so using ``params.get()`` is a must!

Try it out at ``http://localhost:8094/v1/sundistance?name=earth``.


Restricting Parameter Values
============================

Haddock will also allow you to restrict the values of the parameters. Let's change ``sundistance`` to look like the following in ``planets.json``::

    {
        "name": "sundistance",
        "friendlyName": "Distance from the Sun for Planets",
        "endpoint": "sundistance",
        "getProcessors": [
            {
                "versions": [1],
                "requiredParams": [
                    {
                        "param": "name",
                        "paramOptions": ["earth", "pluto"]
                    }
                ],
                "optionalParams": [
                    {
                        "param": "useImperial",
                        "paramOptions": ["yes", "no"]
                    }
                ],
                "returnParams": ["distance"],
                "optionalReturnParams": ["unit"]
            }
        ]
    }

So, instead of giving ``requiredParams`` or ``optionalParams`` a list of strings, we are giving a list of dicts. Each dict **must** have a ``param`` value, the rest are optional. We also specify a ``paramOptions``, which is a list - it can take either dicts or strings, but dicts are only useful when documenting your API through Haddock. Using dicts with it will be covered later, but we only need strings for now.

Since we have only implemented Earth and Pluto, we can now bracket our inputs to those values. Restart ``planets.py`` and try going to ``http://localhost:8094/v1/sundistance?name=jupiter``. You should get something like the following::

    {"status": "fail", "data": "'jupiter' isn't part of [\"earth\", \"pluto\"] in name"}

If an API consumer tries to give an incorrect value, it will respond with an error message - saying that the value given was incorrect, what parameter was incorrect, and what the correct answers are.

``paramOptions`` is valid for both request and return params, optional or otherwise.


List Return Format
==================

Haddock also supports checking a ``list`` of ``dict``s as return values. It will go through each entry of the list and check that the dict contains all of the required values, just like it did above.

Here is a ``sundistance`` that will let us do that::

    {
        "name": "sundistance",
        "friendlyName": "Distance from the Sun for Planets",
        "endpoint": "sundistance",
        "getProcessors": [
            {
                "versions": [1],
                "returnFormat": "list",
                "requiredParams": ["name"],
                "returnParams": ["distance"],
                "optionalReturnParams": ["unit"]
            }
        ]
    }

As you can see, we have added a ``returnFormat`` of ``list``.

And now the ``sundistance_GET`` implementation::

    def sundistance_GET(self, request, params):
        planetName = params["name"].lower()
        sunDistance = self.sunDistance.get(planetName)
        return [
            {"distance": sunDistance["miles"], "unit": "miles"},
            {"distance": sunDistance["smoots"], "unit": "smoots"}
        ]

Then, if you restart ``planets.py`` and go to ``http://localhost:8094/v1/sundistance?name=earth``, you will get the following::

    {"status": "success", "data": [{"distance": 92960000, "unit": "miles"}, {"distance": 87906922100, "unit": "smoots"}]}


Going Further
=============

Next, we'll have a look at implementing authentication into your Haddock API.