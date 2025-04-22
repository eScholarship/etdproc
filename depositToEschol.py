from curses.ascii import ESC
from escholClient import eschol
from dbIntf import etdDb
import json
# work with one package
# call eschol to mint with pubnumber from ProQuest

# this should move to consts
api = eschol()
db = etdDb()
escholId = api.createItem("xyz")

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

    # get the package id
    # if ark entry is already present then return that
    # if no ark then mint and add an entry
    def mint(self):
        print("mint if needed")
        escholId = db.getEscholId(self._pubnum)
        if escholId:
            return escholId
        escholId = api.createItem(self._pubnum)
        db.saveEscholId(self._pubnum, escholId)
        return escholId