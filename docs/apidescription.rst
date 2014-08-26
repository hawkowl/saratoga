Haddock API Description
=======================

The Haddock API Description is a standard structure that Haddock uses to build your API. It contains information about your project (``metadata``), your APIs (``api``), the processors behind those APIs (``getProcessors``/``postProcessors``) and parameters that your API takes and responds with (``parameters`` and ``parameterOptions``).

The API Description ends up having two top-level parts - the ``metadata`` and the ``api``. They are laid out like this::

    {
        "metadata": {
            ...
        },
        "api": {
            ...
        }
    }


Metadata
--------

The ``metadata`` contains three things:

- ``name``: The computer-friendly name.
- ``friendlyName``: The user-friendly name.
- ``versions``: A list of applicable versions. They don't have to be 1, 2, or whatever - they're just used later on in ``api``. Note that there is one special version - "ROOT", which moves all of the endpoints to the root (for example, ``/weather``, instead of ``/v1/weather``).
- ``apiInfo``: Whether or not you want automatic API documentation generated.


API
---

The ``api`` contains a list of dicts, which are API endpoints. In each API method there is:

- ``name``: The computer-friendly name. This is used in naming your functions later!
- ``friendlyName``: The user-friendly name.
- ``description``: The user-friendly description.
- ``endpoint``: The URL endpoint. For example, it will make a processor for v1 be under "/v1/weather".
- ``requiresAuthentication`` (optional): A boolean that defines whether this API needs authentication. Default is false.
- ``rateLimitNumber`` (optional): How many times per unit of time that this API may be called by the API key.
- ``rateLimitTimescale`` (optional): The timescale that the limit number works off, in seconds. For example, a ``rateLimitNumber`` of 10 and a ``rateLimitTimescale`` of 60 means that 10 requests can be made in a sliding window of 60 seconds.
- ``getProcessors`` (optional): A list of processors (see below). These processors respond to a HTTP GET.
- ``postProcessors`` (optional): A list of processors (see below). These processors respond to a HTTP POST.


Processors
----------

Processors are the bits of your API that do things. They are made up of dicts, and contain the following fields:

- ``versions``: A list of versions (see ``metadata``) which this endpoint applies to.
- ``paramsType`` (optional): Where the params will be - either ``url`` (in ``request.args``) or ``jsonbody`` (for example, the body of a HTTP POST). Defaults to ``url``.
- ``returnFormat`` (optional): Either ``dict`` or ``list`` (which means a ``list`` of ``dict``s, conforming to the params below)
- ``requiredParams`` (optional): Parameters that the API consumer *has* to give. This is a list, the contents of which are explained below.
- ``optionalParams`` (optional): Parameters that the API consumer can give, if they want to. This is a list, the contents of which are explained below.
- ``returnParams`` (optional): Parameters that your API *has* to return. This is a list, the contents of which are explained below.
- ``optionalReturnParams`` (optional): Parameters that your API may return. This is a list, the contents of which are explained below.

Please note that if you have set ``requiredParams``, you MUST set every other key that may be given in ``optionalParams``! Same goes with ``returnParams``.


Parameters
----------

When defining the parameters your API can give/take, you can do it two ways. The first way is just giving a string containing the param key, the second is giving it a more detailed ``dict``. The dict fields are below.

- ``param``: The parameter key.
- ``description`` (optional): The user-friendly description of what this parameter is for. This is shown in the API documentation.
- ``type`` (optional): A type that can be displayed in the API documentation. This isn't enforced.
- ``example`` (optional): An example value, for the API documentation.
- ``paramOptions`` (optional): If this parameter can only accept a certain number of values, use this to restrict it to them automatically. It's a list, containing either a string of an acceptable value, or a ``dict`` (details below). These are also shown in the API documentation.


Parameter Options
-----------------

If you want to document your parameter options a bit better than simply giving it values, you can do so by making ``paramOptions`` a list of ``dict``s with the following values:

- ``data``: The acceptable value.
- ``meaning``: The meaning of this value. Used in the API documentation.


Example
-------

For a proper example, see ``betterAPI.json`` under ``haddock/test/``. It has nearly every option defined in there somewhere.