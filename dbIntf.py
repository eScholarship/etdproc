import creds
import mysql.connector
from maps import pqmap, silsmap, campusmap, escholmap, harvestmap


class etdDb:
    queryGatewayMap = "select field1,field2,field3,field4 from settings where settingtype='Gateway'"
    querySilsMap = "select field1,field2,field3,field4,field5,field6,info from settings where settingtype='MarcOut'"
    queryEscholMap = "select field1,field2,info from settings where settingtype='EscholOut'"
    queryHarvestMap = "select field1,field2,field3,field4,field5,field6,info from settings where settingtype='HarvestIn'"
    queryPackage = "select id from packages where pubnum='{param}' and isInvalid = '0'"
    queryAttrs = "select fileattrs, gwattrs, xmlattrs, computedattrs from packages where id= {param}"
    queryXmlAttrs = "select xmlattrs from packages where id='{param}'"
    queryComputedAttrs = "select zipname, pubnum, computedattrs from packages where id ='{param}'"
    queryFileAttrs = "select zipname, fileattrs from packages where id= {param}"
    queryCampusInfo = "select pqcode,code,instloc,namesuffix, nameinmarc, id from campuses"
    queryCampusId = "select id from campuses where code='{param}'"
    queryEscholId = "select escholId from escholrequests where packageId={param}"
    queryQueuedTasks = "select queuename, packageId from queues where queuename != 'done' and RIGHT(queuename, 6) != '-error'"
    queryUnprocessedMCs = "select id, callbackdata from merrittcallbacks where isProcessed = False"
    queryUnprocessedOai = "select identifier, datestamp from harvestlog where isProcessed = False"
    queryPubNumber = "SELECT pubnum FROM packages where id = {param}"
    queryPackageZip = "SELECT id FROM packages where zipname = '{param}'"
    queryDepositResponse = "select depositresponse from escholrequests where packageId={param}"
    queryQueueStatus = "select queuename from queues where packageId = {param}"
    querySilsInLog = "select queuename from queuelogs where queuename = 'sils' and packageId = {param}"
    queryMarcName = "select idvalue from identifiers where packageId = {param} and idtype = 'MarcName'"
    queryConfig = "select ckey, cvalue from config"
    queryHarvestRecord = "select rawvalue from harvestlog where identifier = '{param1}' and datestamp = '{param2}'"
    insertPackage = "insert into packages (pubnum, zipname, campusId) VALUES ('{param1}','{param2}', {param3}) "
    insertMerrittRequest = "insert into merrittrequests (packageId, request, response, currentstatus) VALUES ({param1},'{param2}','{param3}','{param4}') "
    insertEscholRequest = "insert into escholrequests (packageId, escholId) VALUES ({param1},'{param2}')"
    insertQueue = "insert into queues (packageId) VALUES ('{param1}') "
    insertQueueLog = "insert into queuelogs (packageId, queuename) VALUES ({param1}, '{param2}') "
    insertErrorLog = "insert into errorlog (packageId, message, detail) VALUES ({param1},'{param2}','{param3}') "
    insertConfig = "insert into config (ckey, cvalue) VALUES ('{param1}','{param2}') "
    insertIdentifier = "insert into identifiers (packageId, idtype, idvalue) VALUES ({param1},'{param2}','{param3}') "
    insertHarvestRecord = "insert into harvestlog (identifier, datestamp, rawvalue) VALUES (%s, %s, %s) "
    #insertHarvestRecord = "insert into harvestlog (identifier, datestamp, rawvalue) VALUES ('{param1}','{param2}','{param3}') "
    updateEscholRequest = "update escholrequests set depositrequest = '{param2}', actionTime = NOW() where packageId = '{param1}'"
    updateEscholResponse = "update escholrequests set depositresponse = '{param2}', actionTime = NOW() where packageId = '{param1}'"
    updatePubNumCampusId = "update packages set pubnum = '{param2}', campusId = '{param3}', lastUpdated = NOW() where id = '{param1}'"
    updateGwMetadata = "update packages set gwattrs = '{param2}', lastUpdated = NOW() where id = '{param1}'"
    updateXmlMetadata = "update packages set xmlattrs = '{param2}', lastUpdated = NOW() where id = '{param1}'"
    updateComputed = "update packages set computedattrs = '{param2}', lastUpdated = NOW() where id = '{param1}'"
    updateFileAttrs = "update packages set fileattrs = '{param2}', lastUpdated = NOW() where id = '{param1}'"
    updateQueueStatus = "update queues set queuename = '{param2}', actionTime = NOW() where packageId = {param1}"  
    updateMerrittArk = "update packages set computedattrs = JSON_SET(computedattrs, '$.merrittark', '{param2}') where id = {param1}"
    updateEscholArk = "update packages set computedattrs = JSON_SET(computedattrs, '$.escholark', '{param2}') where id = {param1}"
    updateMcProcessed = "update merrittcallbacks set isProcessed = True where id = {param}" 
    updateConfig = "update config set cvalue = '{param2}' where ckey = '{param1}'" 


    def __init__(self):
        self.cnxn = mysql.connector.connect(user=creds.etdDb.username, 
                        password=creds.etdDb.password,
                        host=creds.etdDb.server,
                        database=creds.etdDb.database,
                        charset='utf8mb4',
                        port=creds.etdDb.port, 
                        auth_plugin='mysql_native_password')
        self.cursor = self.cnxn.cursor()

    def getGwSetting(self):
        #print("read parse settings")
        self.cursor.execute(self.queryGatewayMap)
        tagInfo = []
        for row in self.cursor:
            tagInfo.append(pqmap(row[0],row[1],row[2],row[3]))
        return tagInfo

    def getgenerateSetting(self):
        #print("read generate settings")
        self.cursor.execute(self.querySilsMap)
        recordInfo = []
        for row in self.cursor:
            recordInfo.append(silsmap(row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
        return recordInfo

    def getescholSetting(self):
        #print("read eschol settings")
        self.cursor.execute(self.queryEscholMap)
        tagInfo = []
        for row in self.cursor:
            tagInfo.append(escholmap(row[0],row[1],row[2]))
        return tagInfo

    def getoaiSetting(self):
        self.cursor.execute(self.queryHarvestMap)
        tagInfo = []
        for row in self.cursor:
            tagInfo.append(harvestmap(row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
        return tagInfo


    def getConfigs(self):
        print("get configs")
        self.cursor.execute(self.queryConfig)
        rows = self.cursor.fetchall()
        config_dict = {key: value for key, value in rows}
        return config_dict

    def getAttrs(self, packageId):
        #print("read all attrs")
        query = self.queryAttrs.format(param=packageId)
        self.cursor.execute(query)
        for row in self.cursor:
            return (row[0], row[1], row[2], row[3])
        return None
    
    def getCompAttrs(self, packageId):
        #print("read computed attrs")
        query = self.queryComputedAttrs.format(param=packageId)
        self.cursor.execute(query)
        for row in self.cursor:
            return (row[0], row[1], row[2])
        return None

    def getFileAttrs(self, packageId):
        #print("read file attrs")
        query = self.queryFileAttrs.format(param=packageId)
        self.cursor.execute(query)
        for row in self.cursor:
            return (row[0], row[1])
        return None
    def getCampusInfo(self):
        #print("read campus info")
        self.cursor.execute(self.queryCampusInfo)
        attrsInfo = {}
        for row in self.cursor:
            attrsInfo[row[0]] = campusmap(row[1],row[2], row[3], row[4], row[5])
        return attrsInfo

    def getCampusId(self, code):
        #print("read campus id based on campus short name")
        query = self.queryCampusId.format(param=code)
        self.cursor.execute(query)
        campusid = None
        for row in self.cursor:
            campusid = row[0]
        return campusid

    def getUnprocessedMCs(self):
        #print("read unprocessed Merritt Callback")
        self.cursor.execute(self.queryUnprocessedMCs)
        data = {}
        for row in self.cursor:
            data[row[0]] = row[1]
        return data

    def getPubNumber(self, packageId):
        #print("read pub number")
        query = self.queryPubNumber.format(param=packageId)
        self.cursor.execute(query)
        for row in self.cursor:
            return row[0]
        return None

    def savePackage(self, pubnum, zipname, campusId):
        #print("create a new package")
        query = self.insertPackage.format(param1=pubnum, param2= zipname, param3=campusId)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def saveMerrittRequest(self, packageId, requestattrs, responseattrs, status):
        #print("save Merritt request")
        query = self.insertMerrittRequest.format(param1=packageId, param2=requestattrs, param3= responseattrs, param4 = status)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def getPackageId(self,pubnum):
        query = self.queryPackage.format(param=pubnum)
        self.cursor.execute(query)
        for row in self.cursor:
            return row[0]
        return None


    def savePubNumCampusId(self, packageId, pubnum, campusId):
        #print("save pub num")       
        query = self.updatePubNumCampusId.format(param1=packageId, param2 = pubnum, param3 = campusId)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def saveGwMetadata(self, packageId, metadata):
        #print("save marc metadata")       
        query = self.updateGwMetadata.format(param1=packageId, param2 = metadata.replace("'","''").replace('\\','\\\\'))
        self.cursor.execute(query)
        self.cnxn.commit()
        return


    def saveComputedValues(self, packageId, metadata):
        #print("save computed metadata")        
        query = self.updateComputed.format(param1=packageId, param2 = metadata.replace("'","''").replace('\\','\\\\'))
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def savexmlMetadata(self, packageId, metadata):
        #print("save xml metadata")
        query = self.updateXmlMetadata.format(param1=packageId, param2 = metadata.replace("'","''").replace('\\','\\\\'))
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def savefileattrs(self, packageId, fileatts):
        #print("save file attrs")
        query = self.updateFileAttrs.format(param1=packageId, param2 = fileatts)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def getEscholId(self, packageId):
        #print("get eschol id if present")
        query = self.queryEscholId.format(param=packageId)
        self.cursor.execute(query)
        for row in self.cursor:
            return row[0]
        return None

    def getMarcName(self, packageId):
        query = self.queryMarcName.format(param=packageId)
        self.cursor.execute(query)
        for row in self.cursor:
            return row[0]
        return None

    def addEscholRequest(self, packageId, escholId):
        #print("insert a new request")
        query = self.insertEscholRequest.format(param1=packageId, param2 = escholId)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def saveQueue(self, packageId):
        #print("insert queue")
        query = self.insertQueue.format(param1=packageId)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def saveEscholRequest(self, packageId, request):
        #print("save eschol deposit request and response")
        query = self.updateEscholRequest.format(param1=packageId, param2 = request.replace("'","''").replace('\\','\\\\'))
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def saveEscholResponse(self, packageId, response):
        #print("save eschol deposit request and response")
        query = self.updateEscholResponse.format(param1=packageId, param2 = response)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def getAllQueuedTasks(self):
        #print("get any item not yet done")
        self.cursor.execute(self.queryQueuedTasks)
        alltasks = {}
        for row in self.cursor:
            if row[0] not in alltasks:
                alltasks[row[0]] = []
            alltasks[row[0]].append(row[1])

        return alltasks

    def getQueueStatus(self, packageid):
        #print("get queue status")
        query = self.queryQueueStatus.format(param=packageid)
        self.cursor.execute(query)
        for row in self.cursor:
            return row[0]
        return None

    def getxmlAttrs(self, id):
        #print("read xml attrs")
        query = self.queryXmlAttrs.format(param=id)
        self.cursor.execute(query)
        for row in self.cursor:
            return row[0]
        return None

    def saveQueueStatus(self, packageId, newstatus):
        #print("save the new status")
        query = self.updateQueueStatus.format(param1=packageId, param2 = newstatus)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def saveEscholArk(self, packageId, ark):
        #print("save eschol ark")
        query = self.updateEscholArk.format(param1=packageId, param2 = ark)
        self.cursor.execute(query)
        self.cnxn.commit()
        self.saveIdentifier(packageId, "EscholId",ark)
        return    

    def saveMerrittArk(self, packageId, ark):
        #print("save merritt ark")
        query = self.updateMerrittArk.format(param1=packageId, param2 = ark)
        self.cursor.execute(query)
        self.cnxn.commit()
        self.saveIdentifier(packageId, "MerrittArk",ark)
        return   

    def saveErrorLog(self, packageId, error, details):
        #print("save error info")
        query = self.insertErrorLog.format(param1=packageId, param2 = error, param3=details)
        self.cursor.execute(query)
        self.cnxn.commit()
        return   

    def markMCprocessed(self, mcid):
        #print("save merritt ark")
        query = self.updateMcProcessed.format(param=mcid)
        self.cursor.execute(query)
        self.cnxn.commit()
        return   

    def IsZipFilePresent(self, zipname):        
        query = self.queryPackageZip.format(param=zipname)
        self.cursor.execute(query)
        rows = list(self.cursor)  # forces full fetch
        return bool(rows)

    def IsOclcsenddone(self, packageid):
        query = self.querySilsInLog.format(param=packageid)
        self.cursor.execute(query)
        rows = list(self.cursor)  # forces full fetch
        return bool(rows)

    def saveIdentifier(self, packageId, idtype, idvalue):
        #print("save identifier")
        query = self.insertIdentifier.format(param1=packageId, param2 = idtype, param3= idvalue)
        self.cursor.execute(query)
        self.cnxn.commit()
        return
   

    def IsDeposited(self, packageId):
        #print("look for deposit message for this")
        query = self.queryDepositResponse.format(param=packageId)
        self.cursor.execute(query)
        for row in self.cursor:
            return "Deposited." in row[0]
        return False

    def saveQueueLog(self, packageId, status):
        #print("save the current status")
        query = self.insertQueueLog.format(param1=packageId, param2 = status)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def addConfig(self, keyname, value):
        query = self.insertConfig.format(param1=keyname, param2 = value)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def saveConfig(self, keyname, value):
        query = self.updateConfig.format(param1=keyname, param2 = value)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def getHarvestRecord(self, oaiid, stamp):
        query = self.queryHarvestRecord.format(param1=oaiid, param2=stamp)
        self.cursor.execute(query)
        for row in self.cursor:
            return row[0]
        return None

    def addHarvestRecord(self, oaiid, stamp, marcxml):
        self.cursor.execute(self.insertHarvestRecord,(oaiid, stamp, marcxml))
        self.cnxn.commit()
        return

    def getUnprocessedOai(self):
        self.cursor.execute(self.queryUnprocessedOai)
        oaiids = []
        for row in self.cursor:
            oaiids.append((row[0],row[1]))
        return oaiids

    # save harvest attr json

#x = etdDb()
#x.saveQueueLog(1,"eschol")
#x.saveEscholRequest(1, '{"X":"Y"}')
#x.saveGwMetadata(1, '{"X":"Y"}')
#x.saveQueueStatus(1,"Test")
