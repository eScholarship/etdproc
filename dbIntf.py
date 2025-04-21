import creds
import mysql.connector
from maps import pqmap, silsmap, campusmap

# This is temporary connection to get information for sample marc
class jscholDb:
    queryEscholIds = "select id, attrs->'$.local_ids' from items where title ='{param}'"
    queryEmbargoDate = "select status, attrs->'$.embargo_date' from items where id ='{param}'"
    queryKeywords = "select attrs->'$.keywords' from items where id ='{param}'"

    def __init__(self):
        self.cnxn = mysql.connector.connect(user=creds.escholDb.username, 
                        password=creds.escholDb.password,
                        host=creds.escholDb.server,
                        database=creds.escholDb.database,
                        charset='utf8mb4',
                        port=creds.escholDb.port)
        self.cursor = self.cnxn.cursor()

    def getEscholIds(self, title):
        print("read eschol id and local ids")
        query = self.queryEscholIds.format(param=title.replace("'","''").replace('\\','\\\\'))
        self.cursor.execute(query)
        localids = {}
        for row in self.cursor:
            localids[row[0]] = row[1]

        return localids

    def getEmbargoDates(self, id):
        print("read eschol id and local ids")
        query = self.queryEmbargoDate.format(param=id)
        self.cursor.execute(query)
        itemstatus = None
        embargodate = None
        for row in self.cursor:
            itemstatus = row[0]
            embargodate = row[1]

        return itemstatus, embargodate

    def getKeywords(self, id):
        print("read keywords")
        query = self.queryKeywords.format(param=id)
        self.cursor.execute(query)
        keywords = None
        for row in self.cursor:
            keywords = row[0]

        return keywords


class etdDb:
    queryPQMap = "select field1,field2,field3,field4 from settings where settingtype='Gateway'"
    querySilsMap = "select field1,field2,field3,field4,field5,info from settings where settingtype='MarcOut'"
    queryPackage = "select id from packages where pubnum='{param}' and isInvalid = '0'"
    queryAttrs = "select id, gwattrs, xmlattrs, computedattrs from packages where pubnum='{param}' and isInvalid = '0'"
    queryComputedAttrs = "select id, computedattrs from packages where pubnum='{param}' and isInvalid = '0'"
    queryCampusInfo = "select pqcode,code,instloc,namesuffix, nameinmarc from campuses"
    queryCampusId = "select id from campuses where code='{param}'"
    insertPackage = "insert into packages (pubnum, campusId) VALUES ('{param1}',{param2}) "
    insertMerrittRequest = "insert into merrittrequests (packageId, request, response, currentstatus) VALUES ({param1},'{param2}','{param3}','{param4}') "
    updateGwMetadata = "update packages set gwattrs = '{param2}' where id = '{param1}'"
    updateXmlMetadata = "update packages set xmlattrs = '{param2}' where id = '{param1}'"
    updateComputed = "update packages set computedattrs = '{param2}' where id = '{param1}'"
    def __init__(self):
        self.cnxn = mysql.connector.connect(user=creds.etdDb.username, 
                        password=creds.etdDb.password,
                        host=creds.etdDb.server,
                        database=creds.etdDb.database,
                        charset='utf8mb4',
                        port=creds.etdDb.port)
        self.cursor = self.cnxn.cursor()

    def getparseSetting(self):
        print("read parse settings")
        self.cursor.execute(self.queryPQMap)
        tagInfo = []
        for row in self.cursor:
            tagInfo.append(pqmap(row[0],row[1],row[2],row[3]))
        return tagInfo

    def getgenerateSetting(self):
        print("read generate settings")
        self.cursor.execute(self.querySilsMap)
        recordInfo = []
        for row in self.cursor:
            recordInfo.append(silsmap(row[0],row[1],row[2],row[3],row[4],row[5]))
        return recordInfo

    def getAttrs(self, pubnum):
        print("read marc attrs")
        query = self.queryAttrs.format(param=pubnum)
        self.cursor.execute(query)
        for row in self.cursor:
            return (row[1], row[2], row[3])
        return None
    
    def getCompAttrs(self, pubnum):
        print("read computed attrs")
        query = self.queryComputedAttrs.format(param=pubnum)
        self.cursor.execute(query)
        for row in self.cursor:
            return (row[0], row[1])
        return None

    def getCampusInfo(self):
        print("read campus info")
        self.cursor.execute(self.queryCampusInfo)
        attrsInfo = {}
        for row in self.cursor:
            attrsInfo[row[0]] = campusmap(row[1],row[2], row[3], row[4])
        return attrsInfo

    def getCampusId(self, code):
        print("read campus id based on campus short name")
        query = self.queryCampusId.format(param=code)
        self.cursor.execute(query)
        campusid = None
        for row in self.cursor:
            campusid = row[0]
        return campusid

    def savePackage(self, pubnum, campusId):
        print("create a new package")
        query = self.insertPackage.format(param1=pubnum, param2=campusId)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def saveMerrittRequest(self, packageId, requestattrs, responseattrs, status):
        print("save Merritt request")
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

    def saveGwMetadata(self, packageId, metadata):
        print("save marc metadata")       
        query = self.updateGwMetadata.format(param1=packageId, param2 = metadata.replace("'","''").replace('\\','\\\\'))
        self.cursor.execute(query)
        self.cnxn.commit()
        return


    def saveComputedValues(self, packageId, metadata):
        print("save computed metadata")        
        query = self.updateComputed.format(param1=packageId, param2 = metadata.replace("'","''").replace('\\','\\\\'))
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def savexmlMetadata(self, packageId, metadata):
        print("save xml metadata")
        query = self.updateXmlMetadata.format(param1=packageId, param2 = metadata.replace("'","''").replace('\\','\\\\'))
        self.cursor.execute(query)
        self.cnxn.commit()
        return