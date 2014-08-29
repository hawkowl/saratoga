from negotiator import ContentNegotiator, AcceptParameters, ContentType, Language
import json


class OutputRegistry(object):

    def __init__(self):
        self._outputFormats = {}
        self.defaultOutputFormat = None
    
    def getFormat(self, request):

        if request.requestHeaders.hasHeader("Accept"):            
            default_params = AcceptParameters(
                ContentType(self.defaultOutputFormat), Language("en"))

            acceptable = [AcceptParameters(ContentType(x), Language("en")
                                       ) for x in self._outputFormats.keys()]

            cn = ContentNegotiator(default_params, acceptable)

            accp = cn.negotiate(
                accept=request.requestHeaders.getRawHeaders("Accept")[0])

            return str(accp.content_type) if accp else self.defaultOutputFormat

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
        
    
