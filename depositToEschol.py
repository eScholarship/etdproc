
from escholClient import eschol
from dbIntf import etdDb
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
            escholId = api.createItem(self._pubnum)
            db.saveEscholId(self._packageId, self._pubnum, escholId)

        return escholId

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
        response = api.depositItem(depositpackage)
        # save result and response in DB
        db.saveEscholResponse(self._packageId, response)
        # update escholid and url in 
        return depositpackage


x = depositToEschol("30492756")
escholid = x.mint()
#escholid = "ark:/13030/qttt03knt6"
y = x.deposit(escholid)
print(y)
print("done")

