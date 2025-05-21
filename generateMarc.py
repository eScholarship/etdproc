import json
from pymarc import Record, Field, Subfield
from dbIntf import etdDb
import consts


class createMarc:
    _packageId = None
    _gwattrs = None
    _xmlattrs = None
    _compattrs = None
    def __init__(self, packageId):
        self._packageId = packageId
        (gwAttrs, xmlAttrs, compAttrs) = consts.db.getAttrs(packageId)
        self._gwattrs = json.loads(gwAttrs)
        self._xmlattrs = json.loads(xmlAttrs)
        self._compattrs = json.loads(compAttrs)

    def processvalue(self, value, action):
        if action == "dot":
            return value + '.'
        if action == "comma":
            return value + ','
        if action == "escholurl":
            return consts.escholUrlBase + value[-8:]
        return value

    def generateConst(self, setting, fieldtofill):
        print("generate a const field")

        # see if post processing is needed
        value = self.processvalue(setting.info, setting.action)

        # if ind1 and ind2 and field are empty - this is a special case
        if not setting.indicator1 and not setting.indicator2 and not setting.field:
            assert(not fieldtofill)
            return Field(tag=setting.tag, data=value)

        # figure out the indicators
        ind1 = " " if setting.indicator1 == "bl" else setting.indicator1
        ind2 = " " if setting.indicator2 == "bl" else setting.indicator2

        # create a field 
        # TBD - I need to work on creating one field with multiple subfields
        if fieldtofill:
            print("filliing")
            fieldtofill.subfields.append(Subfield(code=setting.field, value=value))
            return None
        else:
            return Field(
                    tag = setting.tag,
                    indicators = [ind1,ind2],
                    subfields = [
                        Subfield(code=setting.field, value=value)
                    ])


    def generateusingAttrs(self, setting, attrs, fieldtofill):
        # if ind1 and ind2 and field are empty - this is a special case
        if not setting.indicator1 and not setting.indicator2 and not setting.field:
            assert(not fieldtofill)
            return Field(tag=setting.tag, data=attrs[setting.sourcefield])

        ind1 = " " if setting.indicator1 == "bl" else setting.indicator1
        ind2 = " " if setting.indicator2 == "bl" else setting.indicator2

        if attrs[setting.sourcefield] is None:
            print("NOT PRESENT " +  setting.sourcefield)
            return None
        # create a field 
        # TBD - I need to work on creating one field with multiple subfields
        if isinstance(attrs[setting.sourcefield], list):
            fields = []
            assert(not fieldtofill)
            for val in attrs[setting.sourcefield]:
                value = self.processvalue(val, setting.action)
                field = Field(
                        tag = setting.tag,
                        indicators = [ind1,ind2],
                        subfields = [
                            Subfield(code=setting.field, value=value)
                        ])
                fields.append(field)
                if (field.tag == '700'):
                    field.subfields.append(Subfield(code='e', value='degree supervisor.'))
                
            return fields

        value = self.processvalue(attrs[setting.sourcefield], setting.action)
        if fieldtofill:
            print("filliing")
            fieldtofill.subfields.append(Subfield(code=setting.field, value=value))
            return None
        else:
            return Field(
                    tag = setting.tag,
                    indicators = [ind1,ind2],
                    subfields = [
                        Subfield(code=setting.field, value=value)
                    ])


    def generateFields(self, setting, lastSetting, lastField):
        print("generate fields")
        # figure out if the last field should be used
        # if not null and has same tag and indicators
        useLastField = False
        if lastSetting and lastField:
                if setting.tag == lastSetting.tag and setting.indicator1 == lastSetting.indicator1 and setting.indicator2 == lastSetting.indicator2:
                    useLastField = True

        # check for embargo date and skip or keep going accordingly
        if setting.tag == '506' and setting.indicator1 == '1' and self._compattrs["embargodate"] is None:
            return None

        # skip 245 indicator other than the matching tilte indicator
        if setting.tag == '245' and setting.indicator2 != self._compattrs["titleIndicator"]:
            return None

        # let's just do this for const
        if setting.sourcefield == 'const':
            fields = self.generateConst(setting, lastField if useLastField else None)
            return fields
    
        if setting.info == 'compute':
            fields = self.generateusingAttrs(setting, self._compattrs, lastField if useLastField else None)
            return fields
        if setting.info == 'xml':
            fields = self.generateusingAttrs(setting, self._xmlattrs, lastField if useLastField else None)
            return fields
        if setting.info == 'gw':
            fields = self.generateusingAttrs(setting, self._gwattrs, lastField if useLastField else None)
            return fields
        return None

    def fixRecordLeader(self, record):
        print("fix record leader")
        record.leader[5] = 'n'
        record.leader[6] = 'a'
        record.leader[7] = 'm'
        record.leader[17] = '7'
        record.leader[18] = 'i'


    # read silsmarc settings
    def generateRecord(self):
        print("generate one record")
        # from pymarc import Record, Field, Subfield
        record = Record()
        lastSetting = None
        lastField = None

        for setting in consts.silsSettings:
            # need to bring the indicator back to '0' after
            fields = self.generateFields(setting, lastSetting, lastField)
            if fields and isinstance(fields, list):
                for field in fields:
                    record.add_field(field)
            if fields and not isinstance(fields, list):
                lastSetting = setting
                lastField = fields
                record.add_field(fields)

        self.fixRecordLeader(record)
        return record


    def writeMarcFile(self):
        record = self.generateRecord()
        filepath = f'{consts.marcDir}/ETDS-{self._xmlattrs["pubNumber"]}.mrc'
        with open(filepath, 'wb') as data:
            data.write(record.as_marc21())
        return filepath

#print("start - create")

#x = createMarc("30492756")
#x.writeMarcFile()

#print("end -- crate")