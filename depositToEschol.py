import os
import json
import time
import shutil
import consts
import pathlib
from escholClient import eschol

api = eschol()
MAX_GRAPHQL_INT = 2_147_483_647  # 2^31 - 1

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
        code, escholId = api.createItem(consts.localIdPrefix + self._pubnum)
        if code == 200:
            consts.db.addEscholRequest(self._packageId, escholId)
            consts.db.saveEscholArk(self._packageId, escholId[-10:])
        else:
            consts.db.saveErrorLog(self._packageId,"Mint operation failed", cleanResponse(escholId))
            raise Exception("Mint operation failed") 
        # Throttle the requests to eSchol API
        time.sleep(1) # pause for 1 sec

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
        # For other files find location in the director tree and also update the byte size in 
        # os.path.getsize(file_path)
        supp_info = {}
        for item in traversepath.rglob("*"):
            if item.is_file():
                if item.name in self._fileattrs["supp"]:
                    print(item.name)
                    print(os.path.getsize(item))                    
                    item_dest = os.path.join(dest_path, item.name)
                    item_size = os.path.getsize(item)
                    # copy the files only if it is less than 2G
                    if item_size < MAX_GRAPHQL_INT:
                        shutil.copy(item, item_dest)
                        supp_info[item.name] = item_size
        return supp_info

    def updateSupp(self, depositpackage, supp_info):
        print("update supp")
        if "suppFiles" in depositpackage:
            for item in depositpackage["suppFiles"]:
                if item["file"] in supp_info:
                    item["size"] = supp_info[item["file"]]
                else: # remove from the supp file list 
                    item["size"] = 0
            depositpackage["suppFiles"] = [item for item in depositpackage["suppFiles"] if item.get("size", 0) != 0]
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
        code, response = api.depositItem(depositpackage)
        print(response)
        # save result and response in DB
        consts.db.saveEscholResponse(self._packageId, cleanResponse(response))
        # was this successfull or not - check the response
        # update escholid and url in 

        if code != 200:
            consts.db.saveErrorLog(self._packageId,"deposit failed", "details in escholrequests table")
            raise Exception("desposit failed") 

        # Throttle the requests to eSchol API
        time.sleep(2) # pause for 2 sec
        return

class replaceEscholMetadata:
    _packageId = None
    _gwattrs = None
    _xmlattrs = None
    _compattrs = None
    _oaioverride = None
    def __init__(self, packageId):
        self._packageId = packageId
        (_, gwAttrs, xmlAttrs, compAttrs) = consts.db.getAttrs(packageId)
        self._gwattrs = json.loads(gwAttrs)
        self._xmlattrs = json.loads(xmlAttrs)
        self._compattrs = json.loads(compAttrs)
        override = consts.db.getOaiOverride(packageId)
        if override:
            self._oaioverride = json.loads(override)

    def replaceMeta(self):
        print("replace metadata")
        # create the replace package
        replacepackage = {}
        for setting in consts.escholSetting:
            # skip contentLink and supp
            if setting.field == 'contentLink' or setting.field == 'contentFileName' or setting.field == 'suppFiles':
                continue
            if setting.typedata == "const":
                replacepackage[setting.field] = setting.info
            elif setting.typedata == "xml" and setting.info in self._xmlattrs and self._xmlattrs[setting.info]:
                replacepackage[setting.field] = self._xmlattrs[setting.info]
            elif setting.typedata == "gw" and setting.info in self._gwattrs and self._gwattrs[setting.info]:
                replacepackage[setting.field] = self._gwattrs[setting.info]
            elif setting.typedata == "compute" and setting.info in self._compattrs and self._compattrs[setting.info]:
                replacepackage[setting.field] = self._compattrs[setting.info]
            # if override exists for the package, make use of the info
            if self._oaioverride and setting.field in self._oaioverride:
                replacepackage[setting.field] = self._oaioverride[setting.field]

        print(replacepackage)
        # call API with replace metadata
        code, response = api.replaceMeta(replacepackage)
        print(response)

        if code != 200:
            consts.db.saveErrorLog(self._packageId,"replace meta failed", cleanResponse(response))
            raise Exception("replacemeta failed") 

        # Throttle the requests to eSchol API
        time.sleep(2) # pause for 2 sec
        return



