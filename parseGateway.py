
import io
import json
import consts
import requests
from creds import pg_creds
from pymarc.marcxml import record_to_xml, parse_xml_to_array


class etdParseGateway:
    _data = None
    _record = None
    _pubNumber = None
    _packageId = None
    gwSettings = None
    # this needs to take packageId instead and obtain corresponding pubnum
    def __init__(self, packageId):
        print("get gw info")
        self._data = {}
        self._record = None
        self._packageId = packageId
        self._pubNumber = consts.db.getPubNumber(packageId)


    def process(self):
        assert(self._pubNumber)
        self.getmarc()
        if self._record:
            self.extractMarcInfo()
            self.saveToDb()
            return True # was able to retrieve data
        return False

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
        #print(response.text)
        # Convert string to file-like object
        marcxml_io = io.StringIO(response.text)
        recorddata = parse_xml_to_array(marcxml_io)
        # since the search is by id - expect one record
        for record in recorddata:
            if record:
                self._record = record
        # let the caller know if okay to proceed

    def saveToDb(self):
        #print("save the xml extracted data in ")
        metadata = json.dumps(self._data,ensure_ascii=False)
        consts.db.saveGwMetadata(self._packageId, metadata)
        # save isbn in identifiers table
        consts.db.saveIdentifier(self._packageId, "ISBN",self._data["isbn"])

    def extractMarcInfo(self):
        #print("start - extract")
        # have the parsing settings from DB
        # save the leader as well
        marcMetadata = {}
    
        for setting in consts.gwSettings:
            # get the tag info
            #print(setting.tag + "  " + setting.field)
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
        #print("done - extract")
        self._data = marcMetadata
        return marcMetadata


#print("start")
#x = etdParseGateway(1)
#x.process()
#print("end")