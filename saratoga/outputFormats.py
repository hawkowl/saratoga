import json

class OutputRegistry(object):

    def __init__(self):
        self._outputFormats = {}
        self.defaultOutputFormat = None
    
    def getFormat(self, request):

        fmtList = []
        
        if request.requestHeaders.hasHeader("Accept"):
            fmtList = request.requestHeaders.getRawHeaders("Accept")[0].split(";")

        for fmt in fmtList:
            if fmt in self._outputFormats:
                return fmt

        return self.defaultOutputFormat

        
    def renderAutomaticResponse(self, request, status, data):

        f = self.getFormat(request)
        return self._outputFormats[f](status, data)

        
    def register(self, acceptHeader, func):
        """
        Register an output format.
        """
        self._outputFormats[acceptHeader] = func

def JSendJSONOutputFormat(status, data):
    """
    Implements the JSend output format, serialised to JSON.
    """

    resp = {
        "status": status,
        "data": data
    }

    return json.dumps(resp)

def DebuggableJSendJSONOutputFormat(status, data):

    resp = {
        "status": status,
        "data": data
    }
    
    return json.dumps(resp, sort_keys=True, indent=4, separators=(',', ': '))
        
    
