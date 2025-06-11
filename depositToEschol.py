import os
import json
import shutil
import consts
import pathlib
# work with one package
# call eschol to mint with pubnumber from ProQuest

def cleanResponse(text):
    # Remove single and double quotes
    text = text.replace("'", "").replace('"', "")
    # Limit string length to 900 characters
    return text[:900]

class mintEscholId:
    _packageId = None
    _pubnum = None
    def __init__(self, packageId):
        self._packageId = packageId
        self._pubnum = consts.db.getPubNumber(packageId)

    def mint(self):
        print("mint if needed")
        # add pubnum from ProQuest as external id
        existingArk = consts.db.getEscholId(self._packageId)
        if existingArk:
            print(f'skipping mint; found {existingArk}')
            return
        code, escholId = consts.api.createItem(self._pubnum)
        if code == 200:
            consts.db.addEscholRequest(self._packageId, escholId)
            consts.db.saveEscholArk(self._packageId, escholId[-10:])
        else:
            consts.db.saveErrorLog(self._packageId,"Mint operation failed", cleanResponse(escholId))
            raise Exception("Mint operation failed") 

        return escholId

class depositToEschol:
    _packageId = None
    _fileattrs = None
    _gwattrs = None
    _xmlattrs = None
    _compattrs = None
    def __init__(self, packageId):
        self._packageId = packageId
        (fileattrs, gwAttrs, xmlAttrs, compAttrs) = consts.db.getAttrs(packageId)
        self._fileattrs = json.loads(fileattrs)
        self._gwattrs = json.loads(gwAttrs)
        self._xmlattrs = json.loads(xmlAttrs)
        self._compattrs = json.loads(compAttrs)

    def copyFilesToDepositDir(self):
        # copy pdf from extract folder to deposit one
        source_path = f'{consts.extractDir}/{self._fileattrs["folder"]}'
        dest_path = f'{consts.depositDir}/{self._fileattrs["folder"]}'  
        os.makedirs(dest_path, exist_ok=True)
        shutil.copy(os.path.join(source_path, self._fileattrs["pdffile"]), os.path.join(dest_path, self._fileattrs["pdffile"]))
        shutil.copy(os.path.join(source_path, self._fileattrs["xmlfile"]), os.path.join(dest_path, self._fileattrs["xmlfile"]))

        traversepath = pathlib.Path(source_path)
        # TBD - For other files find location in the director tree and also update the byte size in 
        # os.path.getsize(file_path)
        supp_info = {}
        for item in traversepath.rglob("*"):
            if item.is_file():
                if item.name in self._fileattrs["supp"]:
                    print(item.name)
                    print(os.path.getsize(item))
                    # copy the files
                    item_dest = os.path.join(dest_path, item.name)
                    item_size = os.path.getsize(item)
                    shutil.copy(item, item_dest)
                    supp_info[item.name] = item_size
        return supp_info

    def updateSupp(self, depositpackage, supp_info):
        print("update supp")
        if "suppFiles" in depositpackage:
            for item in depositpackage["suppFiles"]:
                item["size"] = supp_info[item["file"]]
        return depositpackage


    def deposit(self):
        print("deposit")
        # create the deposit package
        depositpackage = {}
        for setting in consts.escholSetting:
            if setting.typedata == "const":
                depositpackage[setting.field] = setting.info
            elif setting.typedata == "xml" and setting.info in self._xmlattrs and self._xmlattrs[setting.info]:
                depositpackage[setting.field] = self._xmlattrs[setting.info]
            elif setting.typedata == "gw" and setting.info in self._gwattrs and self._gwattrs[setting.info]:
                depositpackage[setting.field] = self._gwattrs[setting.info]
            elif setting.typedata == "compute" and setting.info in self._compattrs and self._compattrs[setting.info]:
                depositpackage[setting.field] = self._compattrs[setting.info]

        supp_info = self.copyFilesToDepositDir()
        depositpackage = self.updateSupp(depositpackage, supp_info)
        # save the package in DB
        consts.db.saveEscholRequest(self._packageId, json.dumps(depositpackage,ensure_ascii=False))
        # call API with deposit package
        code, response = consts.api.depositItem(depositpackage)
        # save result and response in DB
        consts.db.saveEscholResponse(self._packageId, cleanResponse(response))
        # was this successfull or not - check the response
        # update escholid and url in 
        if code != 200:
            consts.db.saveErrorLog(self._packageId,"deposit failed", "details in escholrequests table")
            raise Exception("desposit failed") 
        return


#x = depositToEschol("30492756")
##escholid = x.mint()
#escholid = "ark:/13030/qtttddfsch"
#y = x.deposit(escholid)
#print(y)
#print("done")

