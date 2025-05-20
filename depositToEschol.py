
from escholClient import eschol
from dbIntf import etdDb
from errorLog import CustomError
import json
import consts
# work with one package
# call eschol to mint with pubnumber from ProQuest

def cleanResponse(text):
    # Remove single and double quotes
    text = text.replace("'", "").replace('"', "")
    # Limit string length to 900 characters
    return text[:900]

class mintEscholId:
    _packageId = None
    def __init__(self, packageId):
        self._packageId = packageId

    def mint(self):
        print("mint if needed")
        code, escholId = consts.api.createItem(f'etdproc id {self._packageId}')
        if code == 200:
            consts.db.addEscholRequest(self._packageId, "TBD", escholId)
            consts.db.saveEscholArk(self._packageId, escholId[-10:])
        else:
            raise CustomError("Mint operation failed", cleanResponse(escholId)) 

        return escholId

class depositToEschol:
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


    def deposit(self):
        print("deposit")
        # create the deposit package
        depositpackage = {}
        for setting in consts.escholSetting:
            print(setting)
            if setting.typedata == "const":
                depositpackage[setting.field] = setting.info
            elif setting.typedata == "xml" and setting.info in self._xmlattrs and self._xmlattrs[setting.info]:
                depositpackage[setting.field] = self._xmlattrs[setting.info]
            elif setting.typedata == "gw" and setting.info in self._gwattrs and self._gwattrs[setting.info]:
                depositpackage[setting.field] = self._gwattrs[setting.info]
            elif setting.typedata == "compute" and setting.info in self._compattrs and self._compattrs[setting.info]:
                depositpackage[setting.field] = self._compattrs[setting.info]

        # save the package in DB
        consts.db.saveEscholRequest(self._packageId, json.dumps(depositpackage,ensure_ascii=False))
        # call API with deposit package
        code, response = consts.api.depositItem(depositpackage)
        # save result and response in DB
        consts.db.saveEscholResponse(self._packageId, cleanResponse(response))
        # was this successfull or not - check the response
        # update escholid and url in 
        if code != 200:
            raise CustomError(f'deposit failed for {self._packageId}', "details in escholrequests table")
        return


#x = depositToEschol("30492756")
##escholid = x.mint()
#escholid = "ark:/13030/qtttddfsch"
#y = x.deposit(escholid)
#print(y)
#print("done")

