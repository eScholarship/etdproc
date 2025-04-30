import creds
import mysql.connector
from maps import pqmap, silsmap, campusmap, escholmap


class etdDb:
    queryPQMap = "select field1,field2,field3,field4 from settings where settingtype='Gateway'"
    querySilsMap = "select field1,field2,field3,field4,field5,field6,info from settings where settingtype='MarcOut'"
    queryEscholMap = "select field1,field2,info from settings where settingtype='EscholOut'"
    queryPackage = "select id from packages where pubnum='{param}' and isInvalid = '0'"
    queryAttrs = "select id, gwattrs, xmlattrs, computedattrs from packages where pubnum='{param}' and isInvalid = '0'"
    queryComputedAttrs = "select id, computedattrs from packages where pubnum='{param}' and isInvalid = '0'"
    queryCampusInfo = "select pqcode,code,instloc,namesuffix, nameinmarc from campuses"
    queryCampusId = "select id from campuses where code='{param}'"
    queryEscholId = "select id from escholrequests where pubnum='{param}'"
    insertPackage = "insert into packages (pubnum, campusId) VALUES ('{param1}',{param2}) "
    insertMerrittRequest = "insert into merrittrequests (packageId, request, response, currentstatus) VALUES ({param1},'{param2}','{param3}','{param4}') "
    insertEscholRequest = "insert into escholrequests (packageId, pubnum, escholId) VALUES ({param1},'{param2}','{param3}') "
    updateEscholDeposit = "update escholrequests set depositrequest = '{param2}',depositresponse = '{param3}' where packageId = '{param1}'"
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
            recordInfo.append(silsmap(row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
        return recordInfo

    def getescholSetting(self):
        print("read eschol settings")
        self.cursor.execute(self.queryEscholMap)
        tagInfo = []
        for row in self.cursor:
            tagInfo.append(escholmap(row[0],row[1],row[2]))
        return tagInfo

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

    def getEscholId(self, pubnum):
        print("get eschol id if present")
        query = self.queryEscholId.format(param=pubnum)
        self.cursor.execute(query)
        for row in self.cursor:
            return row[0]
        return None

    def saveEscholId(self, packageId, pubnum, escholId):
        print("save eschol id if present")
        query = self.insertEscholRequest.format(param1=packageId, param2 = pubnum, param3 = escholId)
        self.cursor.execute(query)
        self.cnxn.commit()
        return

    def saveEscholDeposit(self, packageId, request, response):
        print("save eschol deposit request and response")
        query = self.updateEscholDeposit.format(param1=packageId, param2 = request, param3 = response)
        self.cursor.execute(query)
        self.cnxn.commit()
        return
