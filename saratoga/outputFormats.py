from negotiator import ContentNegotiator, AcceptParameters, ContentType
import json


class OutputRegistry(object):

    def __init__(self, defaultOutputFormat):
        self._outputFormats = {}
        self._outputFormatsPreference = []
        self.defaultOutputFormat = defaultOutputFormat
    
    def getFormat(self, request):

        defaultOutput = AcceptParameters(
            ContentType(self.defaultOutputFormat, params='q=0'))
        
        acceptable = [defaultOutput] + [AcceptParameters(ContentType(x)) for x in self._outputFormatsPreference]
        
        cn = ContentNegotiator(defaultOutput, acceptable)
        if request.requestHeaders.hasHeader("Accept"):
            kwargs = {"accept": request.requestHeaders.getRawHeaders("Accept")[0]}
        else:
            kwargs = {}
            
        accp = cn.negotiate(**kwargs)

        return str(accp.content_type) if accp else None

        
    def renderAutomaticResponse(self, request, status, data):

        f = self.getFormat(request)
        return self._outputFormats[f](status, data)

        
    def register(self, acceptHeader, func):
        """
        Register an output format.
        """
        self._outputFormats[acceptHeader] = func
        self._outputFormatsPreference.append(acceptHeader)

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
        
    
