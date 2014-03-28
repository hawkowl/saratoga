import os

__version__ = "0.1.0"

basePath = os.path.abspath(os.path.dirname(__file__))

try:
    from subprocess import check_output
    cmd = "--git-dir={}/../.git".format(basePath)
    res = check_output(["git", cmd, "rev-parse", "--short", "HEAD"])[:-1]
    __version__ = "{} ({})".format(__version__, res)
except Exception, e:
    pass


class APIError(Exception):
    code = 500

    def __init__(self, message, code=None):
        super(APIError, self).__init__(message)

class DoesNotExist(APIError):
    code = 404

class BadRequestParams(APIError):
    code = 400

class BadResponseParams(APIError):
    code = 500

class AuthenticationRequired(BadRequestParams):
    code = 401

class AuthenticationFailed(BadRequestParams):
    code = 403