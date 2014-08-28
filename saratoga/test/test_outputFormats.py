from twisted.trial.unittest import TestCase

from saratoga import api, outputFormats
from saratoga.test.test_api import APIImpl, APIDef

class SaratogaAcceptHeaderTests(TestCase):

    def setUp(self):

        def respJSON(status, data):
            return "JSON"

        def respYAML(status, data):
            return "YAML"

        o = outputFormats.OutputRegistry()
        o.register("application/yaml", respYAML)
        o.register("application/json", respJSON)
        o.register("application/debuggablejson",
                   outputFormats.DebuggableJSendJSONOutputFormat)
        o.defaultOutputFormat = "application/json"
        
        self.api = api.SaratogaAPI(APIImpl, APIDef, outputRegistry = o)

    def test_noneGiven(self):

        def rendered(request):
            self.assertEqual(
                request.getWrittenData(),
                "JSON"
            )

        return self.api.test("/v1/example").addCallback(rendered)

    def test_nonDefaultGiven(self):

        def rendered(request):
            self.assertEqual(
                request.getWrittenData(),
                "YAML"
            )

        return self.api.test("/v1/example",
                             headers={"Accept": ["application/yaml"]}
                         ).addCallback(rendered)

    def test_unknownDefaultGiven(self):
         
        def rendered(request):
            self.assertEqual(
                request.getWrittenData(),
                "JSON"
            )

        return self.api.test("/v1/example",
                             headers={"Accept": ["application/whatever"]}
                         ).addCallback(rendered)

    def test_debuggableJSend(self):
         
        def rendered(request):
            self.assertEqual(
                request.getWrittenData(),
                '{\n    "data": {},\n    "status": "success"\n}'
            )

        return self.api.test("/v1/example",
                             headers={"Accept": ["application/debuggablejson"]}
                         ).addCallback(rendered)
