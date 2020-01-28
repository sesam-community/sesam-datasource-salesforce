from functools import wraps
from flask import Flask, request, Response, abort
from datetime import datetime, timedelta
from dateutil.parser import parse
import os

import json
import pytz
from simple_salesforce import Salesforce
import iso8601
import logging
from collections import OrderedDict

app = Flask(__name__)

logger = None



import asyncio
import time
from threading import Thread
from aiosfstream import SalesforceStreamingClient



thread = Thread()

class Stream(Thread):
    def __init__(self):
        super(Stream, self).__init__()




    def start_stream(self):

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ent = loop.run_until_complete(asyncio.gather(self.stream_events()))

        self.get_ent(ent)
        self.start_stream()



    async def stream_events(self):

        client =  SalesforceStreamingClient(
        consumer_key="<Consumer key>",
        consumer_secret="<Consumer secret>",
        username="<Username>",
        password="<Password>",
        sandbox=True)


        await client.open()# subscribe to topics
        await client.subscribe("/topic/<>")
        await client.subscribe("/topic/<>")


        message = await client.receive()

        return message


    def get_ent(self,ent):
        #print(ent[0]['data']['event']['type'])
        global liste
        if ent[0]['data']['event']['type'] == 'deleted':
            ent[0]['data']['event']['LastModifiedDate'] = datetime_format(datetime.now(pytz.UTC))
        liste.extend(ent)
        #liste = liste[:-256000]
        #print(liste[-1])

    def run(self):
        self.start_stream()


def datetime_format(dt):
    return '%04d' % dt.year + dt.strftime("-%m-%dT%H:%M:%SZ")


def to_transit_datetime(dt_int):
    return "~t" + datetime_format(dt_int)

class DataAccess:
    def __init__(self):
        self._entities = {"Activity": [], "Contact": [], "Account": [], "Lead": [], "Task": [], "Event": [], "Group": [], "Opportunity": [], "User": [], "EventRelation": [], "Case": []}

    def get_entities(self, since, datatype, sf):
        if not datatype in self._entities:
            abort(404)


        if since is None:
            return self.get_entitiesdata(datatype, since, sf)
        else:
            return self.get_entitiesdata(datatype, since, sf)#[entity for entity in self.get_entitiesdata(datatype, since, sf) if entity["_updated"] > since]

    def get_entitiesdata(self, datatype, since, sf):
        # if datatype in self._entities:
        #     if len(self._entities[datatype]) > 0 and self._entities[datatype][0]["_updated"] > "%sZ" % (datetime.now() - timedelta(hours=12)).isoformat():
        #        return self._entities[datatype]
        now = datetime.now(pytz.UTC)
        entities = []
        end = datetime.now(pytz.UTC)  # we need to use UTC as salesforce API requires this
        since = '2020-01-24T14:27:48.711Z'
        if since is None:# start < min(liste[datatype].values()) :
            #fields = getattr(sf, datatype).describe()["fields"]
            result = [x['Id'] for x in sf.query("SELECT Id FROM %s" % (datatype))["records"]]
        else:

            returned = liste

            result,deleted = {},{}
            result[datatype] = {}
            deleted[datatype] = {}
            result[datatype] = {returned[i]['data']['sobject']['Id']:iso8601.parse_date(returned[i]['data']['sobject']['LastModifiedDate']) for i in range(len(liste)) if returned[i]['data']['event']['type'] in ['updated','created'] and returned[i]['channel'].split('/')[-1] == datatype }
            deleted[datatype] = {returned[i]['data']['sobject']['Id']:iso8601.parse_date(returned[i]['data']['event']['LastModifiedDate']) for i in range(len(liste)) if returned[i]['data']['event']['type'] in ['deleted'] and returned[i]['channel'].split('/')[-1] == datatype }
        if since:
            since = iso8601.parse_date(since)
            print(len(result[datatype]))
            if len(result[datatype]) > 0:
                print('in leq test',min(result[datatype].values()))
                if since < min(result[datatype].values()):
                    print('in since')
                    result = [x['Id'] for x in sf.query("SELECT Id FROM %s" % (datatype))["records"]]
            else:
                result = [x['Id'] for x in sf.query("SELECT Id FROM %s" % (datatype))["records"]]


                #if getattr(sf, datatype):
                #    if end > (start + timedelta(seconds=60)):
                #        result = getattr(sf, datatype).updated(start, end)["ids"]
                #        deleted = getattr(sf, datatype).deleted(start, end)["deletedRecords"]


        try: deleted
        except NameError: deleted = None
        if deleted != None:
            print('in deltet')
            deleted = {k:v for (k,v) in deleted[datatype].items() if v > since}
            for ids,time in deleted.items():

                c = OrderedDict({"_id": ids})
                # c = {k: v for k, v in c.items() if v}
                c.update({"_updated": "%s" % time})
                c.update({"_deleted": True})

                entities.append(c)

        try: result
        except NameError: result = None
        if result != None:
            if type(result) == type(dict()):
                result = list({k:v for (k,v) in result[datatype].items() if v > since}.keys())
                if self._entities[datatype] == []:
                    fields = getattr(sf, datatype).describe()["fields"]
                    self._entities[datatype] = fields

                if len(result) < 1:
                    return []
            if len(result) == 1:
                result = [getattr(sf,datatype).get(result[0])]
            else:
                cols = (',').join(list(getattr(sf,datatype).get(result[0]))[1:])
                result = sf.query("SELECT {} FROM {} WHERE Id in ('{}')".format(cols,datatype,("','").join(result)))['records']


            for e in result:

                #c = getattr(sf, datatype).get(e)
                #c = {k: v for k, v in c.items() if v}

                e.update({"_id": e['Id']})
                e.update({"_updated": "%s" % e["LastModifiedDate"]})

                for property, value in e.items():
                    schema = [item for item in self._entities[datatype] if item["name"] == property]
                    if value and len(schema) > 0 and "type" in schema[0] and schema[0]["type"] == "datetime":
                        e[property] = to_transit_datetime(parse(value))


                entities.append(e)


        return entities

data_access_layer = DataAccess()

def get_var(var):
    envvar = None
    if var.upper() in os.environ:
        envvar = os.environ[var.upper()]
    else:
        envvar = request.args.get(var)
    logger.info("Setting %s = %s" % (var, envvar))
    return envvar

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return authenticate()
        return f(*args, **kwargs)

    return decorated


"""
TODO:

    Use OAuth 2.0 for all requests?
"""

@app.route('/<datatype>', methods=['GET'])
@requires_auth
def get_entities(datatype):
    global liste
    since = request.args.get('since')
    instance = get_var('instance') or "prod"
    use_sandbox = True
    if instance == "sandbox":
        use_sandbox = True
        logger.info("Using sandbox")
    auth = request.authorization
    token, username = auth.username.split('\\', 1)
    password = auth.password
    logger.info("User = %s" % (auth.username))

    sf = Salesforce(username, password, token, sandbox=use_sandbox)
    entities = sorted(data_access_layer.get_entities(since, datatype, sf), key=lambda k: k["_updated"])

    resp = json.dumps(entities)

    return Response(resp, mimetype='application/json')



@app.route('/<datatype>', methods=['POST'])
@requires_auth
def receiver(datatype):
    # get entities from request and write each of them to a file
    entities = request.get_json()
    app.logger.info("Updating entity of type %s" % (datatype))
    app.logger.debug(json.dumps(entities))
    instance = get_var('instance') or "prod"
    use_sandbox = True
    if instance == "sandbox":
        use_sandbox = True
        logger.info("Using sandbox")
    auth = request.authorization
    logger.info("User = %s" % (auth.username))
    token, username = auth.username.split('\\', 1)
    sf = Salesforce(username, auth.password, token, sandbox=use_sandbox)


    if getattr(sf, datatype):
        transform(datatype, entities, sf)# create the response
    return Response("Thanks!", mimetype='text/plain')


"""
TODO:
Set up bulk updates to salesfoce to minimize query numbers
"""

def transform(datatype, entities, sf):
    global ids
    # create output directory
    c = None
    listing = []
    if not isinstance(entities, (list)):
        listing.append(entities)
    else:
        listing = entities
    for e in listing:
        app.logger.info("Updateing entity internal id %s of type %s" % (e["_id"], datatype))
        del e["_id"]
        if not ("_deleted" in e and e["_deleted"]):
            if "Id" in e:
                app.logger.debug("Getting entity %s of type %s" % (e["Id"], datatype))
                c = getattr(sf, datatype).get(e["Id"])
            if not c and "sesam_id__c" in e:
                try:
                    c = getattr(sf, datatype).get_by_custom_id("sesam_id__c", e["sesam_id__c"])
                except:
                    pass
            if not c:
                d = []
                for p in e.keys():
                    if p.startswith("_"):
                        d.append(p)
                for p in d:
                    del(e[p])
                if "Id" in e:
                    del (e["Id"])
                getattr(sf, datatype).create(e)
        if "_deleted" in e and e["_deleted"] :
            if "Id" in e:
                app.logger.info("Deleting entity %s of type %s" % (e["Id"],datatype))
                try:
                    getattr(sf, datatype).delete(c["Id"])
                except Exception as err:
                    app.logger.info("Entity %s of type %s does not exist. Ignoring error: %s..." % (e["Id"], datatype, type(err)))
                    pass
        else:
            d = []
            for p in e.keys():
                if p.startswith("_"):
                    d.append(p)
            for p in d:
                del(e[p])
            if "Id" in e:
                del (e["Id"])
            if c:
                getattr(sf, datatype).update(c["Id"], e)


if __name__ == '__main__':

    liste = []
    # Set up logging
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger('salesforce-microservice')

    # Log to stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.DEBUG)

    thread = Stream()
    thread.start()

    app.run(debug=True, host='0.0.0.0')
