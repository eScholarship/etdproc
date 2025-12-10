
from dbIntf import etdDb

# ============================================================
# Create sigleton that are utilized in rest of the application
# DB connection is created and kept alive for all the steps
# for ETD processing 
# ============================================================
db = etdDb()

campusinfo = db.getCampusInfo()
silsSettings = db.getgenerateSetting()
gwSettings = db.getGwSetting()
escholSetting = db.getescholSetting()
oaiSetting = db.getoaiSetting()
configs = db.getConfigs()

downloadDir = '/apps/eschol/etdproc/zip/download'
extractDir = '/apps/eschol/etdproc/zip/extract'
depositDir = '/apps/eschol/apache/htdocs/etdprocTmp/'
doneDir = '/apps/eschol/etdproc/zip/done/'
errorDir = '/apps/eschol/etdproc/zip/error/'
marcDir = '/apps/eschol/etdproc/marc'
localIdPrefix = 'PQPubNum:'
