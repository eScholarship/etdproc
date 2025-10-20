import consts
import json
from lxml import etree
from io import BytesIO
from pymarc import parse_xml_to_array


class processOai:
    def parseMarcInfo(self):
        print("start")
        # should I get unprocessed and null attrs
        allids = consts.db.getUnprocessedOai()
        for (i,d) in allids:
            marcxml = consts.db.getHarvestRecord(i,d)
            #saveInMerritt(marcxml)
            attrs, isInvalid = self.getAttributes(marcxml)
            # find the matching Package id
            packageId = consts.db.getpackagebyisbn(attrs["isbn"])
            # fill attrs and package id
            consts.db.saveHarvestAttr(i,d, json.dumps(attrs,ensure_ascii=False), packageId, isInvalid)
            
            if packageId and not isInvalid:
                consts.db.saveQueueStatus(packageId, "oaiupdate")
        print("end")

    def getAttributes(self, marcxml):
        print("parse xml and get the attributes out")
        marc_stream = BytesIO(marcxml.encode('utf-8'))
        marc_records = parse_xml_to_array(marc_stream)
        attrs = {}
        isWorldCatUpdate = False
        for marc in marc_records:
            for setting in consts.oaiSetting:
                attrs[setting.destfield] = self.getValue(marc,setting)
            isWorldCatUpdate = "908" in marc

        return attrs, isWorldCatUpdate

    def getValue(self, marc, setting):
        if setting.indicator1 == 'bl' and setting.indicator2 == 'bl':
            if setting.field in marc[setting.tag]:
                return marc[setting.tag][setting.field]
            else:
                return None
        else:
            for field in marc.get_fields(setting.tag):
                if field.indicators[0] == setting.indicator1:
                    return field[setting.field]
        return None


# x = processOai()
# x.parseMarcInfo()