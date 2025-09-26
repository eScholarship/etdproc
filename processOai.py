import consts
from lxml import etree
from io import BytesIO
from pymarc import parse_xml_to_array
from sendToMerritt import marcToMerritt

class processOai:
    def parseMarcInfo(self):
        print("start")
        allids = consts.db.getUnprocessedOai()
        for (i,d) in allids:
            marcxml = consts.db.getHarvestRecord(i,d)
            #saveInMerritt(marcxml)
            attrs = self.getAttributes(marcxml)
            # find the matching Package id
            # fill attrs and package id
            # see if there is another record for this package id
            # if so, add the package for oaiupdate queue
            # use the harvest map to complete attrs
        print("end")

    def getAttributes(self, marcxml):
        print("parse xml and get the attributes out")
        marc_stream = BytesIO(marcxml.encode('utf-8'))
        marc_records = parse_xml_to_array(marc_stream)
        attrs = {}
        for marc in marc_records:
            for setting in consts.oaiSetting:
                attrs[setting.destfield] = self.getValue(marc,setting)
        print(attrs)
        return attrs

    def getValue(self, marc, setting):
        if setting.indicator1 == 'bl' and setting.indicator2 == 'bl':
            return marc[setting.tag][setting.field]
        else:
            for field in marc.get_fields(setting.tag):
                if field.indicators[0] == setting.indicator1:
                    return field[setting.field]
        return None
# get all the id and stamp where isProcessed is False

# for each of these, get the raw data and parse the data to extract values and prepare json

# determine the package related to the OAI record 
# save the xml in Merritt - now that the data is in memory. 
# add the package id in queue for oaiupdate queue
# when processing oaiupdate figure out the metadata values to update 
# If there are multiple oai records, then check which fields are updated and then update the corresponding info before adding the article for remeta


# def saveInMerritt(marcxml):
#     print("save xml in Merritt")
#     y = marcToMerritt('ark:/99999/fk4h14st5d', "this")
#     y.sendXmlToMerritt(marcxml)

x = processOai()
x.parseMarcInfo()