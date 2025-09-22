
from dbIntf import etdDb
from escholClient import eschol

# move to const file
db = etdDb()
api = eschol()

campusinfo = db.getCampusInfo()
silsSettings = db.getgenerateSetting()
gwSettings = db.getGwSetting()
escholSetting = db.getescholSetting()
configs = db.getConfigs()

downloadDir = '/apps/eschol/etdproc/zip/download'
extractDir = '/apps/eschol/etdproc/zip/extract'
depositDir = '/apps/eschol/apache/htdocs/etdprocTmp/'
doneDir = '/apps/eschol/etdproc/zip/done/'
errorDir = '/apps/eschol/etdproc/zip/error/'
marcDir = '/apps/eschol/etdproc/marc'
localIdPrefix = 'PQPubNum:'
