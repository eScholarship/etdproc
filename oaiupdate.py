
import consts
import json
from sendToMerritt import marcToMerritt

class OaiUpdate:
    _entries = []
    _newValues = {}
    _oldValues = {}
    _escholValues = {}
    _packageid = None
    _oaiattrs = []

    def __init__(self, packageid):
        print("starting")
        self._entries = consts.db.getlastTwoHarvestEntries(packageid)
        self._packageid = packageid

    def process(self):
        # get all the entries with this package id
        if len(self._entries) == 0:
             raise Exception("No harvest entry found!")
        # if there is only one then nothing else to do
        if len(self._entries) == 1:
            # then there is nothing to do except mark the item processed
            consts.db.saveQueueStatus(self._packageid, "done")
        else:
            self._newValues = json.loads(self._entries[0].attrs)
            self._oldValues = json.loads(self._entries[1].attrs)
            self.addOaiOverride()
            self.saveInMerritt()
            consts.db.saveQueueStatus(self._packageid, "oaioverride")
        # if there are more than one entries, then diff the jsons to find out what has changed
        # based on what has changed, create an entry in oaioverride table
        consts.db.markOaiProcessed(self._entries[0].identifier, self._entries[0].datestamp)
        return

    def saveInMerritt(self):
        print("save xml in Merritt")
        (_, _, attrs) = consts.db.getCompAttrs(self._packageid)
        etdattrs = json.loads(attrs)
        y = marcToMerritt(etdattrs["merrittark"], etdattrs["merrittbucket"])
        marcxml = consts.db.getHarvestRecord(self._entries[0].identifier, self._entries[0].datestamp)
        y.sendXmlToMerritt(marcxml)

    def addOaiOverride(self):
        print("add OAI override")
        for key in self._newValues:
            print(self._newValues[key])
            print(self._oldValues[key])
            if self._newValues[key] != self._oldValues[key]:
                print("need to add to oaioverride")
                # need to save the values as they come and also the transformed entity
                self._oaiattrs.append(key)
        self.fillOverrides()

    def fillOverrides(self):
        print("fill the overrides")
        # need to look at the settings to see 
        for setting in consts.oaiSetting:
            # if the destfield is present in self._oaiattrs
            if setting.destfield in self._oaiattrs:
                self.addEscholValue(setting)

                
        # save the new values and escholvalues in override table
        consts.db.addOaiOverride(self._packageid, json.dumps(self._newValues,ensure_ascii=False), json.dumps(self._escholValues,ensure_ascii=False))

    def addEscholValue(self, setting):
        # TBD need to make sure that the identifiers are not present in the changed things
        value = self._newValues[setting.destfield]
        if setting.action == 'combine':
            # this is for title
            value = self._newValues["maintitle"].strip(" /:")
            if self._newValues["subtitle"]:
                value = value + ": " + self._newValues["subtitle"].strip(" /")
        elif setting.action == "dash":
            # this is for the data, need to bring back dash
            value = f"{value[:4]}-{value[4:6]}-{value[6:]}"

        elif setting.action == "nameparts":
            value = self.getNameparts(setting, value)

        self._escholValues[setting.escholfield] = value

    def getNameparts(self, setting, value):
        result = []
        if setting.destfield == "authors":
            firstsep = ","
            secondsep = " "
        else:
            firstsep = ";"
            secondsep = ","

        namelist = value.split(firstsep)
        for name in namelist:
            splitname = name.split(secondsep)
            x = {"nameparts": ""}
            if setting.destfield == "authors":
                x["nameparts"] = {"fname":splitname[0].strip(',.'),"lname":splitname[1].strip(',.')}
            else:
                x["nameparts"] = {"fname":splitname[1].strip(',.'),"lname":splitname[0].strip(',.')}
                x["role"] = "ADVISOR"

            result.append(x)
        return result

x = OaiUpdate(50)
x.process()
