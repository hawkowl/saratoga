Saratoga API Description
=======================

The Saratoga API Description is a standard structure that Haddock uses to build your API.
It contains information about your project (``metadata``), your API endpoints (``endpoints``), and the processors behind those APIs (``<METHOD>Processors``).

The API Description ends up having two top-level parts - the ``metadata`` and the ``endpoint``. They are laid out like this::

    {
        "metadata": {
            ...
        },
        "endpoints": {
            ...
        }
    }


Metadata
--------

The ``metadata`` contains three things:

- ``name``: The computer-friendly name.
- ``friendlyName``: The user-friendly name.
- ``versions``: A list of applicable versions. They don't have to be 1, 2, or whatever -- they're just used later on in ``api``.


Endpoints
---------

The ``endpoints`` section contains a list of dicts, which are API endpoints. In each API method there is:

- ``name``: The computer-friendly name. This is used in naming your functions later!
- ``friendlyName``: The user-friendly name.
- ``description``: The user-friendly description.
- ``endpoint``: The URL endpoint. For example, it will make a processor for v1 be under ``/v1/weather``.
  Alternatively, it can be a regular expression.
- ``func``: The name that refers to the processor method.
  Required if ``endpoint`` is a regex.
- ``requiresAuthentication`` (optional): A boolean that defines whether this API needs authentication. Default is false.
- ``getProcessors`` (optional): A list of processors (see below). These processors respond to a HTTP GET.
- ``postProcessors`` (optional): A list of processors (see below). These processors respond to a HTTP POST.
- ``putProcessors`` (optional): A list of processors (see below). These processors respond to a HTTP PUT.
- ``deleteProcessors`` (optional): A list of processors (see below). These processors respond to a HTTP DELETE.
- ``patchProcessors`` (optional): A list of processors (see below). These processors respond to a HTTP PATCH.


Processors
----------

Processors are the bits of your API that do things. They are made up of dicts, and contain the following fields:

- ``versions``: A list of versions (see ``metadata``) which this endpoint applies to.
- ``paramsType`` (optional): Where the params will be - either ``url`` (in ``request.args``) or ``jsonbody`` (for example, the body of a HTTP POST). Defaults to ``url``.


Example
-------

For a proper example, see the top of ``saratoga/test/test_api.py``.
It has nearly every option defined in there somewhere.
