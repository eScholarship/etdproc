import consts
import datetime
from sickle import Sickle
from sickle.models import Record
from lxml import etree

class harvertMarc:
    _sickle = None
    _listparams = None

    def __init__(self):
        print("starting")
        self._listparams = {'metadataPrefix' : consts.configs['harvest.prefix'],
            'set': consts.configs['harvest.setname'],
            'from': consts.configs['harvest.fromdate']}
        print(self._listparams)
        self._sickle = Sickle(consts.configs['harvest.url'])

    def getFeedAndSave(self):
        print("get feed and save")
        records = self._sickle.ListRecords(**self._listparams)
        # Iterate through records and print basic info
        for i, record in enumerate(records):
            print(f"\nRecord #{i+1}")
            print("Identifier:", record.header.identifier)
            print("Datestamp:", record.header.datestamp)
            oaiid = record.header.identifier
            stamp = record.header.datestamp.strip('Z')
            if record.header.deleted:
                print("Skipping the deleted record")
                continue
            # Is this record present?
            if consts.db.getHarvestRecord(oaiid, stamp):
                print("Skipping the record is already present in DB")
                continue
            xml_root = etree.fromstring(record.raw.encode('utf-8'))
            metadata_elem = xml_root.find('.//{http://www.openarchives.org/OAI/2.0/}metadata')
            marcxml = etree.tostring(metadata_elem[0], encoding='utf-8')
            # add if it is not present
            consts.db.addHarvestRecord(oaiid, stamp, marcxml)
            #print("Deleted:", record.header.deleted)
            #print("Raw Metadata:\n", record.raw)
            # if the identifier and date 
            # IsHarvestRecordPresent(oaiid, stamp)
            # addHarvestRecord(oaiid, stamp, marcxml_str)

        # once all records are processed, update the date
        currentdate = datetime.date.today().strftime('%Y-%m-%d')
        consts.db.saveConfig('harvest.fromdate', currentdate)

x = harvertMarc()
x.getFeedAndSave()