
from dbIntf import etdDb
from escholClient import eschol

# move to const file
db = etdDb()
api = eschol()

campusinfo = db.getCampusInfo()
silsSettings = db.getgenerateSetting()
gwSettings = db.getGwSetting()
escholSetting = db.getescholSetting()

#downloadDir = '/apps/eschol/etdproc/zip/download'
downloadDir = 'C:/Users/myucekul/Downloads'
extractDir = 'c:/Temp'
#extractDir = '/apps/eschol/etdproc/zip/extract'
doneDir = '/apps/eschol/etdproc/zip/done'
errorDir = '/apps/eschol/etdproc/zip/error'
marcDir = './out'
escholUrlBase = 'https://escholarship.org/uc/item/'
