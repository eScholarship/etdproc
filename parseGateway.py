import requests
from creds import pg_creds
import json
from dbIntf import etdDb
from pymarc.marcxml import record_to_xml, parse_xml_to_array
from maps import pqmap

# need to move this to const file
db = etdDb()

class etdParseGateway:
    _data = None
    _record = None
    _pubNumber = None
    allsettings = None
    # this needs to take packageId instead and obtain corresponding pubnum
    def __init__(self, pubnum):
        print("get the path to the folder where content lives")
        self._data = {}
        self._record = None
        self._pubNumber = pubnum
        self.allsettings = self.readParseInfo()
        self.getmarc()
        self.extractMarcInfo()
        self.saveToDb()

    def getmarc(self):
        print("generate meta data")
        params = {
            'operation': 'searchRetrieve',
            'version': '1.2',
            'maximumRecords': 30,
            'startRecord':1,
            'query':f'rec.identifier="{self._pubNumber}"',
            'x-username':pg_creds.username,
            'x-password':pg_creds.password
        }
        response = requests.get(pg_creds.host, params=params)
        # no need to save
        with open('pq.dat', 'w') as out:
            out.write(response.text)

        with open('pq.dat', 'r') as indata:
            recorddata = parse_xml_to_array(indata)
            # since the search is by id - expect one record
            for record in recorddata:
                if record:
                    self._record = record

    def saveToDb(self):
        print("save the xml extracted data in ")
        # save - xmlmetadata table
        #db = etdDb()
        metadata = json.dumps(self._data,ensure_ascii=False)
        # this needs to move elsewhere
        db.savePackage(self._pubNumber, 1)
        packageid = db.getPackageId(self._pubNumber)
        db.saveGwMetadata(packageid, metadata)
        return

    def readParseInfo(self):
        print("read parse info")
        return db.getparseSetting()

    def extractMarcInfo(self):
        print("start - extract")
        # have the parsing settings from DB
        # save the leader as well
        marcMetadata = {}
    
        for setting in self.allsettings:
            # get the tag info
            print(setting.tag + "  " + setting.field)
            if setting.field == '':
                marcMetadata[setting.attr] = self._record[setting.tag].data
            else:
                if setting.isMulti:
                    marcMetadata[setting.attr] = []
                    for f in self._record.get_fields(setting.tag):
                        marcMetadata[setting.attr].append(f[setting.field])
                else:
                    marcMetadata[setting.attr] = self._record[setting.tag][setting.field]
            #from the record - read that tag
            # if multiple flag is set - iterate through all
        print("done - extract")
        self._data = marcMetadata
        return marcMetadata

    #def saveMarcMetadata(self, metadata, campusId):
    #    print("start - save")
    #    # create package object based in isbn
    #    db.savePackage(metadata['isbn'], campusId)
    #    packageid = db.getPackageId(metadata['isbn'])
    #    #packageid = 3
    #    # create marcmetadata object and save 
    #    db.savemarcMetadata(packageid, json.dumps(metadata,ensure_ascii=False))

print("start")
x = etdParseGateway("30492756")
print("end")