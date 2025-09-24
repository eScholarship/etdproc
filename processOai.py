import consts
from lxml import etree
from io import BytesIO
from pymarc import parse_xml_to_array
from sendToMerritt import marcToMerritt
# get all the id and stamp where isProcessed is False

# for each of these, get the raw data and parse the data to extract values and prepare json

# determine the package related to the OAI record 
# save the xml in Merritt - now that the data is in memory. 
# add the package id in queue for oaiupdate queue
# when processing oaiupdate figure out the metadata values to update 
# If there are multiple oai records, then check which fields are updated and then update the corresponding info before adding the article for remeta
def getAttributes(marcxml):
    print("parse xml and get the attributes out")
    marc_stream = BytesIO(marcxml.encode('utf-8'))
    marc_records = parse_xml_to_array(marc_stream)
    for marc in marc_records:
        print(marc['245']['a'])

def saveInMerritt(marcxml):
    print("save xml in Merritt")
    y = marcToMerritt('ark:/99999/fk4h14st5d', "this")
    y.sendXmlToMerritt(marcxml)

print("start")
allids = consts.db.getUnprocessedOai()
for (i,d) in allids:
    marcxml = consts.db.getHarvestRecord(i,d)
    saveInMerritt(marcxml)
    # use the harvest map to complete attrs
print("end")