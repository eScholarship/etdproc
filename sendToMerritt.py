import creds
import requests
import re
from dbIntf import etdDb
import json
import os
import consts

class marcToMerritt:
    _collection = None
    _marcpath = None
    _merrittark = None
    def __init__(self, marcpath, merrittark):
        print(f'EtdToMerritt start')
        self._marcpath = marcpath   
        self._merrittark = merrittark
        # Merritt collection should come from self._compAttrs["merrittbucket"]
        self._collection = creds.merritt_creds.collection + "_content"# temp for testing

    def sendToMerritt(self):
        files = {
            'file': open(self._marcpath, 'rb'),
            'submitter': (None, creds.merritt_creds.username),
            'responseForm': (None, 'json'),
            'notificationFormat': (None, 'json'),
            'profile': (None, self._collection),
            'primaryIdentifier':(None, self._merrittark),
        }

        # send request
        response = requests.post(creds.merritt_creds.url, files=files, auth=(creds.merritt_creds.username, creds.merritt_creds.password),headers={'Accept': 'application/json'})
        print(response)

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
        self._zipfile = os.path.join( consts.downloadDir, zipfile+".zip")
        # Merritt collection should come from self._compAttrs["merrittbucket"]
        self._collection = creds.merritt_creds.collection + "_content"# temp for testing


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

        print("DONE")

    def sendRequest(self):
        print("create request and send Merritt update")
        files = {
            'file': open(self._zipfile, 'rb'),
            'type':(None, 'container'),
            'submitter': (None, creds.merritt_creds.username),
            'title': (None, re.sub(r'[^a-zA-Z0-9 ]', '', self._etdattrs["maintitle"])), 
            'date':(None, self._etdattrs["pub_date"]),
            'creator': (None, self._etdattrs["creators"]),
            'responseForm': (None, 'json'),
            'notificationFormat': (None, 'json'),
            'profile': (None, self._collection),
            'localIdentifier': (None, self._pubnum),
        }

        # send request
        response = requests.post(creds.merritt_creds.url, files=files, auth=(creds.merritt_creds.username, creds.merritt_creds.password),headers={'Accept': 'application/json'})
        print(response)
        
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
