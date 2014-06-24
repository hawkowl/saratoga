from StringIO import StringIO

from twisted.web import server
from twisted.web.http_headers import Headers
from twisted.web.test.test_web import DummyChannel
from twisted.internet.defer import succeed

import json


def _render(resource, request):
    result = resource.render(request)
    if isinstance(result, str):
        request.write(result)
        request.finish()
        return succeed(None)
    elif result is server.NOT_DONE_YET:
        if request.finished:
            return succeed(None)
        else:
            return request.notifyFinish()
    else:
        raise ValueError("Unexpected return value: %r" % (result,))

def requestMock(path, method="GET", host="localhost", port=8080, isSecure=False,
                body=None, headers=None, args=None, reactor=None):
    """
    requestMock is originally from Klein, with the improvements I made in Klein
    PR #30.
    """
    from mock import Mock
    
    if not headers:
        headers = {}

    if not body:
        body = ''

    if not reactor:
        from twisted.internet import reactor

    request = server.Request(DummyChannel(), False)
    request.site = Mock(server.Site)
    request.gotLength(len(body))
    request.content = StringIO()
    request.content.write(body)
    request.content.seek(0)
    request.args = args
    request.requestHeaders = Headers(headers)
    request.setHost(host, port, isSecure)
    request.uri = path
    request.path = path
    request.prepath = []
    request.postpath = path.split('/')[1:]
    request.method = method
    request.clientproto = 'HTTP/1.1'

    request.setHeader = Mock(wraps=request.setHeader)
    request.setResponseCode = Mock(wraps=request.setResponseCode)

    request._written = StringIO()
    request.finishCount = 0
    request.writeCount = 0

    def produce():
        while request.producer:
            request.producer.resumeProducing()

    def registerProducer(producer, streaming):
        request.producer = producer
        if streaming:
            request.producer.resumeProducing()
        else:
            reactor.callLater(0.0, produce)

    def unregisterProducer():
        request.producer = None

    def finish():
        request.finishCount += 1

        if not request.startedWriting:
            request.write('')

        if not request.finished:
            request.finished = True
            request._cleanup()

    def write(data):
        request.writeCount += 1
        request.startedWriting = True

        if not request.finished:
            request._written.write(data)
        else:
            raise RuntimeError('Request.write called on a request after '
                'Request.finish was called.')

    def getWrittenData():
        return request._written.getvalue()

    request.finish = finish
    request.write = write
    request.getWrittenData = getWrittenData

    request.registerProducer = registerProducer
    request.unregisterProducer = unregisterProducer

    request.processingFailed = Mock(wraps=request.processingFailed)

    return request


def _testItem(resource, path, params=None, method="GET", useBody=True,
              headers=None, replaceEmptyWithEmptyDict=True):

    def _cb(result, request):
        return request

    if useBody:
        if replaceEmptyWithEmptyDict and not params:
            params = {}
        req = requestMock(path, body=json.dumps(params), method=method,
                          headers=headers)
    else:
        req = requestMock(path, args=params, method=method,
            headers=headers)

    d = _render(resource, req)
    d.addCallback(_cb, req)
    return d
