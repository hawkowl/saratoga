import json
from saratoga.api import SaratogaAPI

class PlanetAPI(object):
    class v1(object):
        def yearlength_GET(self, request, params):
            planetName = params["params"]["name"].lower()
            if planetName == "earth":
                return {"seconds": 31536000}
            elif planetName == "pluto":
                return {"seconds": 7816176000}

APIDescription = json.load(open("planets.json"))
myAPI = SaratogaAPI(PlanetAPI, APIDescription)
myAPI.run(port=8094)
