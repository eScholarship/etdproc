
from dbIntf import etdDb

# move to const file
db = etdDb()
campusinfo = db.getCampusInfo()
silsSettings = db.getgenerateSetting()
gwSettings = db.getGwSetting()

#downloadDir = '/apps/eschol/etdproc/zip/download'
downloadDir = 'C:/Users/myucekul/Downloads'
extractDir = 'c:/Temp'
#extractDir = '/apps/eschol/etdproc/zip/extract'
doneDir = '/apps/eschol/etdproc/zip/done'
errorDir = '/apps/eschol/etdproc/zip/error'
escholUrlBase = 'https://escholarship.org/uc/item/'
