from sickle import Sickle
from sickle.models import Record
from pymarc import parse_xml_to_array
from lxml import etree
from io import BytesIO

# Initialize the OAI-PMH client
sickle = Sickle('https://uclibraries.alma.exlibrisgroup.com/view/oai/01UCS_NETWORK/request')

from_date = '2025-09-01'
listparams = {'metadataPrefix' : 'marc21',
              'set': 'UCETDs',
              'from': '2025-09-15'}

# Harvest records from a specific set and metadata format
#records = sickle.ListRecords(metadataPrefix='marc21', set='UCETDs',from=from_date)
records = sickle.ListRecords(**listparams)

# Iterate through records and print basic info
for i, record in enumerate(records):
    print(f"\nRecord #{i+1}")
    print("Identifier:", record.header.identifier)
    print("Datestamp:", record.header.datestamp)
    #print("Deleted:", record.header.deleted)
    #print("Raw Metadata:\n", record.raw)
    try:
        xml_root = etree.fromstring(record.raw.encode('utf-8'))
        metadata_elem = xml_root.find('.//{http://www.openarchives.org/OAI/2.0/}metadata')
        marcxml_str = etree.tostring(metadata_elem[0], encoding='utf-8')
        marc_stream = BytesIO(marcxml_str)
        marc_records = parse_xml_to_array(marc_stream)
        for marc in marc_records:
            print(marc['245']['a'])
            #print(marc['506'])
            #print(marc['024'])
            #print(marc['856'])

            for field in marc.get_fields('506'):
                print(f'Field is {field}')
            for field in marc.get_fields('024'):
                print(f'Field is {field}')
                if field.indicators[0] == '8':
                    print(field['a'])
    except Exception as e:
        print(e)
        print("Error parsing MARCXML:", e)
    

