=====================================
Introduction - Getting Off The Ground
=====================================

Saratoga was made to help you create simple APIs that divide cleanly over versions, with minimal fuss -- Saratoga takes care of routing, assembly, parameter checking and authentication for you.
All you have to do is provide your business logic.


Installing
==========

To install, use pip::
    
    $ pip install saratoga

This'll install Saratoga and its base dependencies.
You can also install the ``httpsig`` package to enable HMAC authentication, which will be covered later.


A Very Simple Example
=====================

In this introduction, we will create a *Planet Information* API.
We will create something that will allow us to query it, and will return some information about planets.
So, first, let's define our API.


Simple API Definition
---------------------

Put the following in ``planets.json``::

    {
        "metadata": {
            "name": "planetinfo",
            "friendlyName": "Planet Information",
            "versions": [1]
        },
        "endpoints": [
            {
                "name": "yearlength",
                "friendlyName": "Year Length of Planets",
                "endpoint": "yearlength",
                "getProcessors": [
                    {
                        "versions": [1]
                    }
                ]
            }
        ]
    }

Now, we have made a ``metadata`` section that gives three things:

- The 'name' of our API.
- The 'friendly name' (human-readable) name of our API.
- A list of versions that our API has (right now, just "1").

We then define an ``endpoints`` section, which is a list of our different APIs.
We have defined only one here, and we have said that:

- It has a name of 'yearlength'.
- It has a human-readable name of 'Year Length of Planets'.
- It has an endpoint of 'yearlength'.
  Saratoga structures APIs as ``/<VERSION>/<ENDPOINT>``, so this means that a v1 of it will be at ``/v1/yearlength``.

There is also then ``getProcessors`` -- a list of *processors*.
A processor in Saratoga is the code that actually does the heavy lifting.
This one here only has one item in it, a list of versions that this processor applies to (in this case, just ``1``).

Using this API description, we can figure out that our future API will be at ``/v1/yearlength``.

Now, lets make the processor behind it.


Simple Python Implementation
----------------------------

Put the following in ``planets.py``:

.. code:: python

    import json
    from saratoga.api import SaratogaAPI

    class PlanetAPI(object):
        class v1(object):
            def yearlength_GET(self, request, params):
                pass

    APIDescription = json.load(open("planets.json"))
    myAPI = SaratogaAPI(PlanetAPI, APIDescription)
    myAPI.run(port=8094)

This example can be this brief because Saratoga takes care of nearly everything else.

So, let's break it down. 

1. First we import ``SaratogaAPI`` from ``saratoga.api`` -- this is what takes care of creating your API from the config.
2. We then create a ``PlanetAPI`` class, and make a subclass called ``v1``.
   This corresponds to version 1 of your API.
3. We then create a method called ``yearlength_GET``.
   This is done in a form of ``<NAME>_<METHOD>``.
   It has three parameters - ``self`` (this is special, we'll get to it later), ``request`` (the Twisted Web Request for the API call) and ``params`` (rather than have to parse them yourself, Saratoga does this for you).

Currently, ``yearlength_GET`` does nothing, so lets fill in some basic functionality -- for brevity, we'll only support Earth and Pluto.

.. code::

    def yearlength_GET(self, request, params):
        planetName = params["params"]["name"].lower()
        if planetName == "earth":
            return {"seconds": 31536000}
        elif planetName == "pluto":
            return {"seconds": 7816176000}

As you can see, we access ``params``, which is a dict of all the things given to you in the API call.
This is sorted out by Saratoga, according to your API description -- it makes sure that all required parameters are there, and throws an error if it is not.

We then return a ``dict`` with our result.
Saratoga will automatically serialise it to JSON for consumption, although you can use :doc:`different output formats </outputFormats.html>` if you want a different format.


Running
-------

Let's try and run it!

.. code:: sh

   $ python planets.py

Now, go to ``http://localhost:8094/v1/yearlength?name=earth`` in your web browser. You should get the following back:

.. code:: json

    {
        "data": {
            "seconds": 31536000
	},
	"status": "success"
    }


Going Further
=============

The next article is about adding global state to your Saratoga API.
