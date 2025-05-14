
from escholClient import eschol
from dbIntf import etdDb
from errorLog import CustomError
import json
# work with one package
# call eschol to mint with pubnumber from ProQuest

# this should move to consts
api = eschol()
db = etdDb()
#escholId = api.createItem("xyz")
escholSetting = db.getescholSetting()
class depositToEschol:
    _pubnum = None
    _packageId = None
    _gwattrs = None
    _xmlattrs = None
    _compattrs = None
    def __init__(self, pubnum):
        self._pubnum = pubnum
        (self._packageId, etdattrs) = db.getCompAttrs(pubnum)
        (gwAttrs, xmlAttrs, compAttrs) = db.getAttrs(pubnum)
        self._gwattrs = json.loads(gwAttrs)
        self._xmlattrs = json.loads(xmlAttrs)
        self._compattrs = json.loads(compAttrs)

    def mint(self):
        print("mint if needed")
        escholId = db.getEscholId(self._pubnum)
        if not escholId:
            code, escholId = api.createItem(self._pubnum)
            if code == 200:
                db.saveEscholRequest(self._packageId, self._pubnum, escholId)
            else:
                raise CustomError("Mint operation failed", self.cleanResponse(escholId)) 

        return escholId

    def cleanResponse(self, text):
        # Remove single and double quotes
        text = text.replace("'", "").replace('"', "")
        # Limit string length to 900 characters
        return text[:900]

    def deposit(self, escholId):
        print("deposit")
        # create the deposit package
        depositpackage = {}
        for setting in escholSetting:
            print(setting)
            if setting.typedata == "const":
                depositpackage[setting.field] = setting.info
            elif setting.typedata == "xml" and setting.info in self._xmlattrs and self._xmlattrs[setting.info]:
                depositpackage[setting.field] = self._xmlattrs[setting.info]
            elif setting.typedata == "gw" and setting.info in self._gwattrs and self._gwattrs[setting.info]:
                depositpackage[setting.field] = self._gwattrs[setting.info]
            elif setting.typedata == "compute" and setting.info in self._compattrs and self._compattrs[setting.info]:
                depositpackage[setting.field] = self._compattrs[setting.info]

        depositpackage["id"] = escholId
        # save the package in DB
        db.saveEscholRequest(self._packageId, json.dumps(depositpackage,ensure_ascii=False))
        # call API with deposit package
        code, response = api.depositItem(depositpackage)
        # save result and response in DB
        db.saveEscholResponse(self._packageId, self.cleanResponse(response))
        # was this successfull or not - check the response
        # update escholid and url in 
        if code != 200:
            raise CustomError(f'deposit failed for {escholId}', "details in escholrequests table")
        return depositpackage


x = depositToEschol("30492756")
#escholid = x.mint()
escholid = "ark:/13030/qtttddfsch"
y = x.deposit(escholid)
print(y)
print("done")

