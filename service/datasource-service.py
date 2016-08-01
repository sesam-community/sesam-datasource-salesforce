from flask import Flask, request, Response, abort
from datetime import datetime, timedelta
import urllib, xmltodict
import json

app = Flask(__name__)

cordinates = [{'x': 5, 'y': 59}, {'x': 5, 'y': 59.5}, {'x': 5, 'y': 60}, {'x': 5, 'y': 60.5}, {'x': 5, 'y': 61}, {'x': 5, 'y': 61.5}, {'x': 5, 'y': 62}, {'x': 5, 'y': 62.5}, {'x': 5.5, 'y': 59}, {'x': 5.5, 'y': 59.5}, {'x': 5.5, 'y': 60}, {'x': 5.5, 'y': 60.5}, {'x': 5.5, 'y': 61}, {'x': 5.5, 'y': 61.5}, {'x': 5.5, 'y': 62}, {'x': 5.5, 'y': 62.5}, {'x': 6, 'y': 59}, {'x': 6, 'y': 59.5}, {'x': 6, 'y': 60}, {'x': 6, 'y': 62.5}, {'x': 6, 'y': 63}, {'x': 6.5, 'y': 60.5}, {'x': 6.5, 'y': 61}, {'x': 6.5, 'y': 62.5}, {'x': 6.5, 'y': 63}, {'x': 7, 'y': 58}, {'x': 7, 'y': 60.5}, {'x': 7, 'y': 61}, {'x': 7, 'y': 63}, {'x': 7.5, 'y': 58}, {'x': 7.5, 'y': 61}, {'x': 7.5, 'y': 61.5}, {'x': 7.5, 'y': 62.5}, {'x': 7.5, 'y': 63}, {'x': 7.5, 'y': 63.5}, {'x': 8, 'y': 58}, {'x': 8, 'y': 61}, {'x': 8, 'y': 63}, {'x': 8, 'y': 63.5}, {'x': 8.5, 'y': 58}, {'x': 8.5, 'y': 63}, {'x': 8.5, 'y': 64}, {'x': 9, 'y': 58.5}, {'x': 9, 'y': 63.5}, {'x': 9, 'y': 64}, {'x': 9.5, 'y': 58.5}, {'x': 9.5, 'y': 64}, {'x': 9.5, 'y': 64.5}, {'x': 10, 'y': 59}, {'x': 10, 'y': 63.5}, {'x': 10, 'y': 64}, {'x': 10, 'y': 64.5}, {'x': 10.5, 'y': 59}, {'x': 10.5, 'y': 59.5}, {'x': 10.5, 'y': 63.5}, {'x': 10.5, 'y': 64.5}, {'x': 10.5, 'y': 65}, {'x': 11, 'y': 59}, {'x': 11, 'y': 64.5}, {'x': 11, 'y': 65}, {'x': 11, 'y': 65.5}, {'x': 11.5, 'y': 59}, {'x': 11.5, 'y': 64}, {'x': 11.5, 'y': 64.5}, {'x': 11.5, 'y': 65}, {'x': 11.5, 'y': 65.5}, {'x': 11.5, 'y': 66}, {'x': 11.5, 'y': 68}, {'x': 12, 'y': 65.5}, {'x': 12, 'y': 66}, {'x': 12, 'y': 66.5}, {'x': 12, 'y': 67}, {'x': 12, 'y': 67.5}, {'x': 12, 'y': 68}, {'x': 12.5, 'y': 65.5}, {'x': 12.5, 'y': 66}, {'x': 12.5, 'y': 66.5}, {'x': 12.5, 'y': 67}, {'x': 12.5, 'y': 67.5}, {'x': 12.5, 'y': 68}, {'x': 13, 'y': 66}, {'x': 13, 'y': 66.5}, {'x': 13, 'y': 67}, {'x': 13, 'y': 67.5}, {'x': 13, 'y': 68.5}, {'x': 13.5, 'y': 66.5}, {'x': 13.5, 'y': 67}, {'x': 13.5, 'y': 67.5}, {'x': 13.5, 'y': 68}, {'x': 13.5, 'y': 68.5}, {'x': 14, 'y': 67}, {'x': 14, 'y': 67.5}, {'x': 14, 'y': 68}, {'x': 14, 'y': 68.5}, {'x': 14, 'y': 69}, {'x': 14.5, 'y': 67.5}, {'x': 14.5, 'y': 68}, {'x': 14.5, 'y': 68.5}, {'x': 14.5, 'y': 69}, {'x': 15, 'y': 68}, {'x': 15, 'y': 68.5}, {'x': 15, 'y': 69}, {'x': 15, 'y': 69.5}, {'x': 15.5, 'y': 67.5}, {'x': 15.5, 'y': 69}, {'x': 15.5, 'y': 69.5}, {'x': 16, 'y': 69}, {'x': 16, 'y': 69.5}, {'x': 16, 'y': 70}, {'x': 16.5, 'y': 68}, {'x': 16.5, 'y': 68.5}, {'x': 16.5, 'y': 69}, {'x': 16.5, 'y': 69.5}, {'x': 16.5, 'y': 70}, {'x': 17, 'y': 68.5}, {'x': 17, 'y': 69}, {'x': 17, 'y': 69.5}, {'x': 17, 'y': 70}, {'x': 17, 'y': 70.5}, {'x': 17.5, 'y': 68.5}, {'x': 17.5, 'y': 69}, {'x': 17.5, 'y': 69.5}, {'x': 17.5, 'y': 70}, {'x': 17.5, 'y': 70.5}, {'x': 18, 'y': 69}, {'x': 18, 'y': 69.5}, {'x': 18, 'y': 70}, {'x': 18, 'y': 70.5}, {'x': 18.5, 'y': 69.5}, {'x': 18.5, 'y': 70}, {'x': 18.5, 'y': 70.5}, {'x': 19, 'y': 69.5}, {'x': 19, 'y': 70.5}, {'x': 19.5, 'y': 69.5}, {'x': 19.5, 'y': 70}, {'x': 19.5, 'y': 70.5}, {'x': 20, 'y': 69.5}, {'x': 20, 'y': 70}, {'x': 20, 'y': 70.5}, {'x': 20.5, 'y': 69.5}, {'x': 20.5, 'y': 70}, {'x': 20.5, 'y': 70.5}, {'x': 21, 'y': 69.5}, {'x': 21, 'y': 70}, {'x': 21, 'y': 70.5}, {'x': 21.5, 'y': 70}, {'x': 21.5, 'y': 70.5}, {'x': 22, 'y': 70}, {'x': 22, 'y': 70.5}, {'x': 22.5, 'y': 70}, {'x': 22.5, 'y': 70.5}, {'x': 23, 'y': 70}, {'x': 23, 'y': 70.5}, {'x': 23.5, 'y': 70}, {'x': 24, 'y': 70.5}, {'x': 25, 'y': 70.5}, {'x': 25.5, 'y': 70.5}, {'x': 26.5, 'y': 70.5}, {'x': 27, 'y': 70.5}, {'x': 27.5, 'y': 70.5}, {'x': 28, 'y': 70.5}, {'x': 28.5, 'y': 70.5}, {'x': 29, 'y': 70}, {'x': 29.5, 'y': 70}, {'x': 30, 'y': 70}, {'x': 30.5, 'y': 70}, {'x': 30.5, 'y': 70.5}]

divfactor = 2

startLong = 5 * divfactor
endLong = 31 * divfactor
startLat = 58 * divfactor
endLat = 71 * divfactor


class DataAccess:
    def __init__(self):
        self._entities = {"stationinfo": [], "location": [], "highlow": []}


    def get_entities(self, since, datatype):
        if not datatype in self._entities:
            abort(404)
        if since is None:
            return self.get_entitiesdata(datatype, since)
        else:
            return [entity for entity in self.get_entitiesdata(datatype, since) if entity["_updated"] > since]

    def get_entitiesdata(self, datatype, since):
        if datatype in self._entities:
            if len(self._entities[datatype]) > 0 and self._entities[datatype][0]["_updated"] > "%sZ" % (datetime.now() - timedelta(hours=12)).isoformat():
               return self._entities[datatype]
        now = datetime.now()
        start = since
        if since is None:
            start = (now - timedelta(days=365)).isoformat()
        entities = []
        if datatype == "highlow":
            for c in cordinates:
                file = urllib.request.urlopen(
                    "http://api.sehavniva.no/tideapi.php?lat=%s&lon=%s&fromtime=%sZ&totime=%sZ&datatype=tab&refcode=cd&place=&file=&lang=nn&interval=60&dst=0&tzone=0&tide_request=locationdata" % (
                        c["y"], c["x"], start, (now + timedelta(days=31)).isoformat()))
                data = file.read()
                file.close()

                locationData = xmltodict.parse(data)["tide"]["locationdata"]
                if "location" in locationData:
                    for e in locationData["data"]["waterlevel"]:
                        e["@time"] = e["@time"].replace("+00:00", "Z")
                        e.update({"_id": "%s_%s_%s" % (c["y"] , c["x"], e["@time"])})
                        e.update({"location_id": "%s_%s" % (c["y"] , c["x"])})
                        e.update({"_updated": "%sZ" % now.isoformat()})
                        e.update({"type": locationData["data"]["@type"]})

                        entities.append(e)
                        
        if datatype == "location":
            for c in cordinates:
                file = urllib.request.urlopen(
                    "http://api.sehavniva.no/tideapi.php?lat=%s&lon=%s&refcode=cd&place=&file=&lang=en&tide_request=locationlevels" % (
                    c["y"] , c["x"]))
                data = file.read()
                file.close()

                locationData = xmltodict.parse(data)
                if "tide" in locationData:
                    locationData = xmltodict.parse(data)["tide"]["locationlevel"]
                    if "location" in locationData:
                        locationData.update({"_id": "%s_%s" % (c["y"] , c["x"])})
                        locationData.update({"_updated": "%sZ" % now.isoformat()})

                        entities.append(locationData)

        if datatype == "stationinfo":
            file = urllib.request.urlopen(
                'http://api.sehavniva.no/tideapi.php?type=perm&tide_request=stationlist')
            data = file.read()
            file.close()

            entities = xmltodict.parse(data)["tide"]["stationinfo"]["location"]
            for e in entities:
                e.update({"_id": e["@code"]})
                e.update({"_updated": "%sZ" % now.isoformat()})

        self._entities[datatype] = entities
        return self._entities[datatype]

data_access_layer = DataAccess()

@app.route('/<datatype>')
def get_entities(datatype):
    since = request.args.get('since')
    entities = data_access_layer.get_entities(since, datatype)
    return Response(json.dumps(entities), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

