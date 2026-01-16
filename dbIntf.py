import creds
import mysql.connector
from maps import pqmap, silsmap, campusmap, escholmap, harvestmap, harvestEntry

# ============================================================
# Class Name: etdDb
# Description:
#     Purpose of this class is to encapsulate DB operation functionlity.
#     All SQL statements related to ETD processing are here.   
#
# ============================================================
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
    queryUnprocessedOai = "select identifier, datestamp from harvestlog where isProcessed = False and attrs is null"
    queryPubNumber = "SELECT pubnum FROM packages where id = {param}"
    queryPackageZip = "SELECT id FROM packages where zipname = '{param}'"
    queryDepositResponse = "select depositresponse from escholrequests where packageId={param}"
    queryQueueStatus = "select queuename from queues where packageId = {param}"
    querySilsInLog = "select queuename from queuelogs where queuename = 'sils' and packageId = {param}"
    queryMarcName = "select idvalue from identifiers where packageId = {param} and idtype = 'MarcName'"
    queryConfig = "select ckey, cvalue from config"
    queryHarvestRecord = "select rawvalue from harvestlog where identifier = '{param1}' and datestamp = '{param2}'"
    queryIdentifer = "select packageid from identifiers where idvalue = '{param1}' and idtype = '{param2}'"
    queryHarvestEntries = "select identifier, datestamp, attrs, isProcessed from harvestlog where packageId = {param} and isInvalid = False order by datestamp desc limit 2"
    queryOaiOverride = "select escholattrs from oaioverride where packageId = {param} order by actionTime desc limit 1"
    querydonefolders = "select zipname from packages where id in (select packageId from queues where queuename = 'done' and actionTime < NOW() - INTERVAL 30 DAY);"
    queryQueueCounts = "select queuename, count(*) from queues group by queuename"
    insertPackage = "insert into packages (pubnum, zipname, campusId) VALUES ('{param1}','{param2}', {param3}) "
    insertMerrittRequest = "insert into merrittrequests (packageId, request, response, currentstatus) VALUES ({param1},'{param2}','{param3}','{param4}') "
    insertEscholRequest = "insert into escholrequests (packageId, escholId) VALUES ({param1},'{param2}')"
    insertQueue = "insert into queues (packageId) VALUES ('{param1}') "
    insertQueueLog = "insert into queuelogs (packageId, queuename) VALUES ({param1}, '{param2}') "
    insertErrorLog = "insert into errorlog (packageId, message, detail) VALUES ({param1},'{param2}','{param3}') "
    insertConfig = "insert into config (ckey, cvalue) VALUES ('{param1}','{param2}') "
    insertIdentifier = "insert into identifiers (packageId, idtype, idvalue) VALUES ({param1},'{param2}','{param3}') "
    insertHarvestRecord = "insert into harvestlog (identifier, datestamp, rawvalue) VALUES (%s, %s, %s) "
    insertOaiOverride = "insert into oaioverride (packageId, marcattrs, escholattrs) VALUES (%s, %s, %s) "
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
    updateHarvestAttrs = "update harvestlog set attrs = %s, packageId = %s, isInvalid = %s where identifier = %s and datestamp = %s"
    updateOaiProcessed = "update harvestlog set isProcessed = 1 where identifier = '{param1}' and datestamp = '{param2}'"

    # ============================================================
    # Obtain connection and cursor for the application. This class is
    # a singleton for ETDproc 
    # ============================================================
    def __init__(self):
        self.cnxn = mysql.connector.connect(user=creds.etdDb.username, 
                        password=creds.etdDb.password,
                        host=creds.etdDb.server,
                        database=creds.etdDb.database,
                        charset='utf8mb4',
                        port=creds.etdDb.port, 
                        auth_plugin='mysql_native_password')
        self.cursor = self.cnxn.cursor()

    # ============================================================
    # Obtain gateway settings and save in on object 
    # ============================================================
    def getGwSetting(self):
        #print("read parse settings")
        self.cursor.execute(self.queryGatewayMap)
        tagInfo = []
        for row in self.cursor:
            tagInfo.append(pqmap(row[0],row[1],row[2],row[3]))
        return tagInfo

    # ============================================================
    # Obtain SILS settings and save in an object
    # ============================================================
    def getgenerateSetting(self):
        #print("read generate settings")
        self.cursor.execute(self.querySilsMap)
        recordInfo = []
        for row in self.cursor:
            recordInfo.append(silsmap(row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
        return recordInfo


    # ============================================================
    # Load eschol settings in one object
    # ============================================================
    def getescholSetting(self):
        #print("read eschol settings")
        self.cursor.execute(self.queryEscholMap)
        tagInfo = []
        for row in self.cursor:
            tagInfo.append(escholmap(row[0],row[1],row[2]))
        return tagInfo


    # ============================================================
    # Load OAI related settings and return in one object 
    # ============================================================
    def getoaiSetting(self):
        self.cursor.execute(self.queryHarvestMap)
        tagInfo = []
        for row in self.cursor:
            tagInfo.append(harvestmap(row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
        return tagInfo

    # ============================================================
    # Configuration and creds related to various data systems in kept in
    # DB. Load the key value pairs for the app 
    # ============================================================
    def getConfigs(self):
        print("get configs")
        self.cursor.execute(self.queryConfig)
        rows = self.cursor.fetchall()
        config_dict = {key: value for key, value in rows}
        return config_dict

    # ============================================================
    # Retries all attributes from packages table for a specific packageId 
    # ============================================================
    def getAttrs(self, packageId):
        #print("read all attrs")
        query = self.queryAttrs.format(param=packageId)
        self.cursor.execute(query)
        for row in self.cursor:
            return (row[0], row[1], row[2], row[3])
        return None
    
    # ============================================================
    # Retrieve computed attributes for an ETD by packageId
    # ============================================================
    def getCompAttrs(self, packageId):
        #print("read computed attrs")
        query = self.queryComputedAttrs.format(param=packageId)
        self.cursor.execute(query)
        for row in self.cursor:
            return (row[0], row[1], row[2])
        return None

    # ============================================================
    # Retrieve file attrbutes for an ETD 
    # ============================================================
    def getFileAttrs(self, packageId):
        #print("read file attrs")
        query = self.queryFileAttrs.format(param=packageId)
        self.cursor.execute(query)
        for row in self.cursor:
            return (row[0], row[1])
        return None

    # ============================================================
    # Load attributes related to campus. Campus info is saved in 
    # dictionary by pqcode for campus 
    # ============================================================
    def getCampusInfo(self):
        #print("read campus info")
        self.cursor.execute(self.queryCampusInfo)
        attrsInfo = {}
        for row in self.cursor:
            attrsInfo[row[0]] = campusmap(row[1],row[2], row[3], row[4], row[5])
        return attrsInfo

    # def getCampusId(self, code):
    #     #print("read campus id based on campus short name")
    #     query = self.queryCampusId.format(param=code)
    #     self.cursor.execute(query)
    #     campusid = None
    #     for row in self.cursor:
    #         campusid = row[0]
    #     return campusid

    # ============================================================
    # Read unprocessed Merritt Callback entries 
    # ============================================================
    def getUnprocessedMCs(self):
        #print("read unprocessed Merritt Callback")
        self.cursor.execute(self.queryUnprocessedMCs)
        data = {}
        for row in self.cursor:
            data[row[0]] = row[1]
        return data

    # ============================================================
    # Retried pubnum associated with an ETD by its packageId 
    # ============================================================
    def getPubNumber(self, packageId):
        #print("read pub number")
        query = self.queryPubNumber.format(param=packageId)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()  # forces full fetch
        for row in rows:
            return row[0]
        return None


    # ============================================================
    # Create a new entry in package table for new ETD 
    # ============================================================
    def savePackage(self, pubnum, zipname, campusId):
        #print("create a new package")
        query = self.insertPackage.format(param1=pubnum, param2= zipname, param3=campusId)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Save Merritt request and response for troubleshooting when needed 
    # ============================================================
    def saveMerrittRequest(self, packageId, requestattrs, responseattrs, status):
        #print("save Merritt request")
        query = self.insertMerrittRequest.format(param1=packageId, param2=requestattrs, param3= responseattrs, param4 = status)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Retrieve package id by pub number 
    # ============================================================
    def getPackageId(self,pubnum):
        query = self.queryPackage.format(param=pubnum)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()  # forces full fetch
        for row in rows:
            return row[0]
        return None

    # ============================================================
    # Save pub number and campus id. This functionality is needed
    # for the scenario when xml fails to get parsed. An entry for 
    # the package is created but the result of the info is filled 
    # in when parsing issue is resolved. 
    # ============================================================
    def savePubNumCampusId(self, packageId, pubnum, campusId):
        #print("save pub num")       
        query = self.updatePubNumCampusId.format(param1=packageId, param2 = pubnum, param3 = campusId)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Save parsed data from Gateway in packages table 
    # ============================================================
    def saveGwMetadata(self, packageId, metadata):
        #print("save marc metadata")       
        query = self.updateGwMetadata.format(param1=packageId, param2 = metadata.replace("'","''").replace('\\','\\\\'))
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Save computed values for an ETD in packages table
    # ============================================================
    def saveComputedValues(self, packageId, metadata):
        #print("save computed metadata")        
        query = self.updateComputed.format(param1=packageId, param2 = metadata.replace("'","''").replace('\\','\\\\'))
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Save xml metadata in packages table
    # ============================================================
    def savexmlMetadata(self, packageId, metadata):
        #print("save xml metadata")
        query = self.updateXmlMetadata.format(param1=packageId, param2 = metadata.replace("'","''").replace('\\','\\\\'))
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Save file attributes for an ETD 
    # ============================================================
    def savefileattrs(self, packageId, fileatts):
        #print("save file attrs")
        query = self.updateFileAttrs.format(param1=packageId, param2 = fileatts)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Retrieve eschol ark/id associated with an ETD
    # ============================================================
    def getEscholId(self, packageId):
        #print("get eschol id if present")
        query = self.queryEscholId.format(param=packageId)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()  # forces full fetch
        for row in rows:
            return row[0]
        return None

    # ============================================================
    # Name of indiviual marc file is saved in identies table.
    # Lookup that name for putting together marc records for set of 
    # packages to send combined MARC to SILS
    # ============================================================
    def getMarcName(self, packageId):
        query = self.queryMarcName.format(param=packageId)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()  # forces full fetch
        for row in rows:
            return row[0]
        return None

    # ============================================================
    # Create an entry for eschol deposit for ETD. 
    # Mint step obtains escholId. The id is saved for later use with deposit call.
    # ============================================================
    def addEscholRequest(self, packageId, escholId):
        #print("insert a new request")
        query = self.insertEscholRequest.format(param1=packageId, param2 = escholId)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Create a queue entry for an ETD. The queue entry stores the
    # current state or step for ETD. History of all steps taken
    # for ETD and timestamps are in another table queuelogs.  
    # ============================================================
    def saveQueue(self, packageId):
        #print("insert queue")
        query = self.insertQueue.format(param1=packageId)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # As part of eschol deposit, save the request package
    # ============================================================
    def saveEscholRequest(self, packageId, request):
        #print("save eschol deposit request and response")
        query = self.updateEscholRequest.format(param1=packageId, param2 = request.replace("'","''").replace('\\','\\\\'))
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Save response from eschol. Useful for troubleshooting 
    # ============================================================
    def saveEscholResponse(self, packageId, response):
        #print("save eschol deposit request and response")
        query = self.updateEscholResponse.format(param1=packageId, param2 = response)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Get all queued items where actions is needed. These are all
    # items where queue status is not done or one of the error states
    # In case of error, one needs to investigate the reason for failure
    # and update the state to appropriate retry state to proceed. 
    # ============================================================
    def getAllQueuedTasks(self):
        #print("get any item not yet done")
        self.cursor.execute(self.queryQueuedTasks)
        alltasks = {}
        for row in self.cursor:
            if row[0] not in alltasks:
                alltasks[row[0]] = []
            alltasks[row[0]].append(row[1])

        return alltasks

    # ============================================================
    # This functionality is for fillMerrittArk script. That script is 
    # needed when Merritt deposit is successful but callback is rejected
    # by load balancer. 
    # ============================================================
    def getQueueStatus(self, packageid):
        #print("get queue status")
        query = self.queryQueueStatus.format(param=packageid)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()  # forces full fetch
        for row in rows:
            return row[0]
        return None

    # ============================================================
    # Retrive the attributes parsed from ProQuest xml
    # ============================================================
    def getxmlAttrs(self, id):
        #print("read xml attrs")
        query = self.queryXmlAttrs.format(param=id)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()  # forces full fetch
        for row in rows:
            return row[0]
        return None

    # ============================================================
    # Update status/current step of ETD 
    # ============================================================
    def saveQueueStatus(self, packageId, newstatus):
        #print("save the new status")
        query = self.updateQueueStatus.format(param1=packageId, param2 = newstatus)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Save eschol id/ark in both packages table and identies.  
    # ============================================================
    def saveEscholArk(self, packageId, ark):
        #print("save eschol ark")
        query = self.updateEscholArk.format(param1=packageId, param2 = ark)
        self.cursor.execute(query)
        self.cnxn.commit()
        self.saveIdentifier(packageId, "EscholId",ark)
        return    

    # ============================================================
    # Save Merritt ark in packages and identies tables
    # ============================================================
    def saveMerrittArk(self, packageId, ark):
        #print("save merritt ark")
        query = self.updateMerrittArk.format(param1=packageId, param2 = ark)
        self.cursor.execute(query)
        self.cnxn.commit()
        self.saveIdentifier(packageId, "MerrittArk",ark)
        return   

    # ============================================================
    # Some errors are saved in errors table. Most cases, the error
    # details are in logs. Datestamp for queue item in error state
    # is a way to find the right log file to review for error investigation 
    # ============================================================
    def saveErrorLog(self, packageId, error, details):
        #print("save error info")
        query = self.insertErrorLog.format(param1=packageId, param2 = error, param3=details)
        self.cursor.execute(query)
        self.cnxn.commit()
        return   

    # ============================================================
    # When Merritt callback is parsed and appropriate action taken, 
    # it is marked processed.
    # ============================================================
    def markMCprocessed(self, mcid):
        #print("save merritt ark")
        query = self.updateMcProcessed.format(param=mcid)
        self.cursor.execute(query)
        self.cnxn.commit()
        return   

    # ============================================================
    # This check to prevent duplication. Look for ETD entry based
    # on the ProQuest zip filename 
    # ============================================================
    def IsZipFilePresent(self, zipname):        
        query = self.queryPackageZip.format(param=zipname)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()  # forces full fetch
        return bool(rows)

    # ============================================================
    # If MARC record is already send to OCLC, then skip that record.
    # It is possible to change queue state of ETD to sils to send it again. 
    # This check safeguards against that. If there is a need to resend, the 
    # related entry needs to be removed from queuelogs to get past this check 
    # ============================================================
    def IsOclcsenddone(self, packageid):
        query = self.querySilsInLog.format(param=packageid)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()  # forces full fetch
        return bool(rows)

    # ============================================================
    # All identifiers related to an ETD are saved in table for 
    # purpose of providing visiblity and troubleshooting
    # ============================================================
    def saveIdentifier(self, packageId, idtype, idvalue):
        #print("save identifier")
        query = self.insertIdentifier.format(param1=packageId, param2 = idtype, param3= idvalue)
        self.cursor.execute(query)
        self.cnxn.commit()
        return
   
    # ============================================================
    # Reviews the response from escholAPI to determine if ETD has been deposited 
    # ============================================================
    def IsDeposited(self, packageId):
        #print("look for deposit message for this")
        query = self.queryDepositResponse.format(param=packageId)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()  # forces full fetch
        for row in rows:
            return "Deposited." in row[0]
        return False

    # ============================================================
    # Queuelog contains histroy of all steps taken for ETD and related
    # timestamps. Insert an entry for package id and queue status 
    # ============================================================
    def saveQueueLog(self, packageId, status):
        #print("save the current status")
        query = self.insertQueueLog.format(param1=packageId, param2 = status)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # This functionality for one time setup of populating configs in DB
    # ============================================================
    def addConfig(self, keyname, value):
        query = self.insertConfig.format(param1=keyname, param2 = value)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Updates a config info. This is currently used for OAI harvest
    # functionlity saving update fromdate 
    # ============================================================
    def saveConfig(self, keyname, value):
        query = self.updateConfig.format(param1=keyname, param2 = value)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    #  OAI harvest entries are saved by OAI id and timestamp. Retrieve
    #  one harvest entry for further processing. 
    # ============================================================
    def getHarvestRecord(self, oaiid, stamp):
        query = self.queryHarvestRecord.format(param1=oaiid, param2=stamp)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()  # forces full fetch
        for row in rows:
            return row[0]
        return None

    # ============================================================
    # Save harvest entry from ALMA OAI feed. At this point the entry
    # is not associate to a known ETD. That happens after marc is parsed 
    # ============================================================
    def addHarvestRecord(self, oaiid, stamp, marcxml):
        self.cursor.execute(self.insertHarvestRecord,(oaiid, stamp, marcxml))
        self.cnxn.commit()
        return

    # ============================================================
    # Obtain OAI entries to parse and extract attributes 
    # ============================================================
    def getUnprocessedOai(self):
        self.cursor.execute(self.queryUnprocessedOai)
        oaiids = []
        for row in self.cursor:
            oaiids.append((row[0],row[1]))
        return oaiids

    # ============================================================
    # OAI feed contains ISBN number and that identifier is used to 
    # match OAI feed to package/ ETD 
    # ============================================================
    def getpackagebyisbn(self, isbn):
        query = self.queryIdentifer.format(param1=isbn, param2="ISBN")
        self.cursor.execute(query)
        result = None
        for row in self.cursor:
            result = row[0]
        return result

    # ============================================================
    # Saved parsed OAI harvest data along with its mapping to package 
    # ============================================================
    def saveHarvestAttr(self, i, d, attrs, packageId, isInvalid):
        self.cursor.execute(self.updateHarvestAttrs, (attrs, packageId, isInvalid, i, d))
        self.cnxn.commit()
        return

    # ============================================================
    # There can be multiple OAI feed entries for a package as updates
    # are served by ALMA. This function shares lastest two for diff
    # to determine the changes to send to eschol 
    # ============================================================
    def getlastTwoHarvestEntries(self, packageId):
        query = self.queryHarvestEntries.format(param=packageId)
        self.cursor.execute(query)
        entries = []
        for row in self.cursor:
            entries.append(harvestEntry(row[0],row[1], row[2], row[3]))
        return entries

    # ============================================================
    # Marc harvested OAI entry as processed
    # ============================================================
    def markOaiProcessed(self, i, d):
        query = self.updateOaiProcessed.format(param1=i, param2=d)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    # ============================================================
    # Add override entry for metadata update to eschol
    # ============================================================
    def addOaiOverride(self, packageId, marcValues, escholValues):
        self.cursor.execute(self.insertOaiOverride,(packageId, marcValues, escholValues))
        self.cnxn.commit()
        return

    # ============================================================
    # Get the latest override entry for metadata update to eschol
    # ============================================================
    def getOaiOverride(self, packageId):
        query = self.queryOaiOverride.format(param=packageId)
        self.cursor.execute(query)
        result = None
        for row in self.cursor:
            result = row[0]
        return result

    # ============================================================
    # Find those items completed 'done' in last 30 days
    # ============================================================
    def getOldDoneFolders(self):
        self.cursor.execute(self.querydonefolders)
        folder = []
        for row in self.cursor:
            folder.append(row[0])
        return folder

    # ============================================================
    # Print the current state of queues
    # ============================================================   
    def printqueryQueueCounts(self):
        print("Queue State")
        self.cursor.execute(self.queryQueueCounts)
        for row in self.cursor:
            print(row)


# x = etdDb()
# x.printqueryQueueCounts()
#x.saveQueueLog(1,"eschol")
#x.saveEscholRequest(1, '{"X":"Y"}')
#x.saveGwMetadata(1, '{"X":"Y"}')
#x.saveQueueStatus(1,"Test")
