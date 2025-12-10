
import io
import json
import consts
import requests
from pymarc.marcxml import record_to_xml, parse_xml_to_array

# ============================================================
# Class Name: etdParseGateway
# Description:
#     Query ProQuest gateway for info on specific ETD by pubnum.
#
# Attributes:
#     packageId (int): Id of the ETD in packages table.
#
#
# Usage:
#     x = etdParseGateway(packageId)
#     x.process()
#
# Notes:
#     - It is possible that ProQuest return multiple records. 
#     Need to look at specific field to make sure the record corresponds to ETD
# ============================================================
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
            'x-username':consts.configs['pg_creds.username'],
            'x-password':consts.configs['pg_creds.password']
        }
        response = requests.get(consts.configs['pg_creds.host'], params=params)
        #print(response.text)
        # Convert string to file-like object
        marcxml_io = io.StringIO(response.text)
        recorddata = parse_xml_to_array(marcxml_io)
        # since the search is by id - expect one record
        for record in recorddata:
            if record is not None and self.isThesisRecord(record):
                # check to make sure this record belong to thesis
                self._record = record
        # let the caller know if okay to proceed


    def isThesisRecord(self, record):
        if "260" in record and "b" in record["260"]:
            if "ProQuest Dissertations & Theses" in record["260"]["b"]:
                return True

        return False

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

        #print("done - extract")
        self._data = marcMetadata
        return marcMetadata


# print("start")
# x = etdParseGateway(16)
# x.process()
# print("end")