from saratoga import BadRequestParams, BadResponseParams, AuthenticationRequired


def _verifyResponseParams(result, APIInfo):

    returnFormat = APIInfo.get("responseFormat", "dict")

    if returnFormat == "dict":
        if not isinstance(result, dict):
            raise BadResponseParams("Result did not match the response format.")

        _checkResponseParamsDict(result, APIInfo)

    elif returnFormat == "list":
        if isinstance(result, basestring):
            items = json.loads(result)
        else:
            items = result

        if not isinstance(items, list):
            raise BadResponseParams("Result did not match the response format.")

        for item in items:
            _checkResponseParamsDict(item, APIInfo)

    return result

def _normaliseParams(params):

    finishedParams = []
    paramKeys = []

    for param in params:
        if isinstance(param, dict):
            options = []
            if param.get("paramOptions", None):
                for option in param.get("paramOptions", None):
                    if isinstance(option, dict):
                        options.append(option["data"])
                    elif isinstance(option, basestring):
                        options.append(option)

            paramKeys.append(param["param"])
            finishedParams.append({
                "param": param["param"],
                "paramOptions": options
            })
        elif isinstance(param, basestring):
            paramKeys.append(param)
            finishedParams.append({
                "param": param,
            })

    return (finishedParams, set(paramKeys))

def _checkParamOptions(item, data, exp):

    paramOptions = item.get("paramOptions", None)

    if paramOptions and not data in paramOptions:
        raise exp(
            "'%s' isn't part of %s in %s" % (data, json.dumps(paramOptions),
            item["param"]))

def _checkResponseParamsDict(result, processor):

    if result:
        keys = set(result.keys())
    else:
        keys = set()

    requiredInput = processor.get("requiredResponseParams", set())
    optionalInput = processor.get("optionalResponseParams", set())

    if not requiredInput and not optionalInput:
        return result

    required, requiredKeys = _normaliseParams(requiredInput)
    optional, optionalKeys = _normaliseParams(optionalInput)
    accountedFor = set()

    for key, data in result.iteritems():
        for req in required + optional:
            if req["param"] == key:
                _checkParamOptions(req, data, BadResponseParams)
                accountedFor.add(req["param"])

    missing = requiredKeys - accountedFor
    extra = keys - (requiredKeys | optionalKeys)

    if missing:
        raise BadResponseParams("Missing response parameters: '%s'" % (
            "', '".join(sorted(missing))))
    if extra:
        raise BadResponseParams("Unexpected response parameters: '%s'" % (
            "', '".join(sorted(extra))))

    return True

def _getParams(params, APIInfo):

    if params:
        keys = set(params.keys())
    else:
        keys = set()
        params = {}

    requiredInput = APIInfo.get("requiredParams", set())
    optionalInput = APIInfo.get("optionalParams", set())

    required, requiredKeys = _normaliseParams(requiredInput)
    optional, optionalKeys = _normaliseParams(optionalInput)

    if not requiredInput and not optionalInput:
        return params

    accountedFor = set()

    for key, data in params.iteritems():
        for req in required + optional:
            if req["param"] == key:
                _checkParamOptions(req, data, BadRequestParams)
                accountedFor.add(req["param"])

    missing = requiredKeys - accountedFor
    extra = keys - (requiredKeys | optionalKeys)

    if missing:
        raise BadRequestParams("Missing request parameters: '%s'" % (
            "', '".join(sorted(missing))))
    if extra:
        raise BadRequestParams("Unexpected request parameters: '%s'" % (
            "', '".join(sorted(extra))))

    return params