
import re
import os
import json
import consts
import time
import requests
from io import BytesIO


# ============================================================
# Sends individual ETD MARC21 files to Merritt
# ============================================================
def getMerrittCollection(bucket):
    collection = bucket
    if 'merritt_creds.collection' in consts.configs:
        print("Using test Merritt collection")
        collection = consts.configs['merritt_creds.collection']
    return collection + "_content"

class marcToMerritt:
    _collection = None
    _merrittark = None
    def __init__(self, merrittark, merrittbucket):
        print(f'EtdToMerritt start') 
        self._merrittark = merrittark
        self._collection = getMerrittCollection(merrittbucket)

    def sendFileToMerritt(self, marcpath):
        files = {
            'file': open(marcpath, 'rb'),
            'submitter': (None, consts.configs['merritt_creds.username']),
            'responseForm': (None, 'json'),
            'notificationFormat': (None, 'json'),
            'profile': (None, self._collection),
            'primaryIdentifier':(None, self._merrittark),
        }

        # send request
        response = requests.post(consts.configs['merritt_creds.url'], files=files, auth=(consts.configs['merritt_creds.username'], consts.configs['merritt_creds.password']),headers={'Accept': 'application/json'})
        print(response.text)
        # Throttle the requests to Merritt
        time.sleep(1) # pause for 1 sec

    def sendXmlToMerritt(self, marcxml):
        files = {
            'file': ('oclcmarc.xml', BytesIO(marcxml.encode('utf-8'))),
            'submitter': (None, consts.configs['merritt_creds.username']),
            'responseForm': (None, 'json'),
            'notificationFormat': (None, 'json'),
            'profile': (None, self._collection),
            'primaryIdentifier':(None, self._merrittark),
        }

        # send request
        response = requests.post(consts.configs['merritt_creds.url'], files=files, auth=(consts.configs['merritt_creds.username'], consts.configs['merritt_creds.password']),headers={'Accept': 'application/json'})
        print(response.text)
        # Throttle the requests to Merritt
        time.sleep(1) # pause for 1 sec


class etdToMerritt:
    _zipfile = None
    _pubnum = None
    _collection = None
    _packageId = None
    _etdattrs = None
    _requestattrs = None
    _responseattrs = None
    def __init__(self, packageId):
        print(f'EtdToMerritt start')
        self._packageId = packageId        
        (zipfile, self._pubnum, etdattrs) = consts.db.getCompAttrs(packageId)
        self._etdattrs = json.loads(etdattrs)
        self._zipfile = os.path.join( consts.doneDir, zipfile+".zip")
        self._collection = getMerrittCollection(self._etdattrs["merrittbucket"])


    def process(self):
        status = "processing"
        try:
            self.sendRequest()
            status = "sent"
        except Exception as e:
            # save error message in db
            self._responseattrs = str(e)
            status = "send-error"
            raise
        finally:
            consts.db.saveMerrittRequest(self._packageId, self._requestattrs, self._responseattrs, status)
            # Throttle the requests to Merritt
            time.sleep(2) # pause for 2 sec


        print("DONE")

    def sendRequest(self):
        print("create request and send Merritt update")
        files = {
            'file': open(self._zipfile, 'rb'),
            'type':(None, 'container'),
            'submitter': (None, consts.configs['merritt_creds.username']),
            'title': (None, re.sub(r'[^a-zA-Z0-9 ]', '', self._etdattrs["maintitle"].replace("'", "").replace('"', ""))), 
            'date':(None, self._etdattrs["pub_date"]),
            'creator': (None, self._etdattrs["creators"].replace("'", "").replace('"', "")),
            'responseForm': (None, 'json'),
            'notificationFormat': (None, 'json'),
            'profile': (None, self._collection),
            'localIdentifier': (None, consts.localIdPrefix + self._pubnum),
        }

        # send request
        response = requests.post(consts.configs['merritt_creds.url'], files=files, auth=(consts.configs['merritt_creds.username'], consts.configs['merritt_creds.password']),headers={'Accept': 'application/json'})
        print(response.text)
        
        # save the request info
        files['file'] = None
        
        self._requestattrs = json.dumps(files)
        # save response
        self._responseattrs = response.text
        return

#zipfile = 'C:/Temp/test/zip/etdadmin_upload_1032621.zip'
#assert(os.path.exists(zipfile))
#x = EtdToMerritt(zipfile, "30492756")
#x.process()
#x  = getMerrittCollection("ucsd_lib_etd")
#print(x)
