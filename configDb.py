
import creds
import mysql.connector
import csv

class configDb:
    #allSqlFiles = ["campuses.sql","packages.sql","actionlog.sql","errorlog.sql","settings.sql","identifiers.sql","merrittcallback.sql","merrittrequest.sql"]
    allSqlFiles = ["escholrequest.sql"]
    sqlpath = 'sqlscripts/'
    datapath = 'appdata/' #TBD
    InsertCampus = "INSERT INTO Campuses (code,instloc,pqcode,namesuffix,escholunit,merrittcol,nameinmarc) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    InsertMarcIn = "INSERT INTO settings (settingtype,field1,field2,field3,field4) VALUES (%s,%s,%s,%s,%s)"
    InsertSilsMap = "INSERT INTO settings (settingtype,field1,field2,field3,field4,field5,field6,info) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    InsertEscholMap = "INSERT INTO settings (settingtype,field1,field2,info) VALUES (%s,%s,%s,%s)"
    def __init__(self):
        self.cnxn = mysql.connector.connect(user=creds.etdDb.username, 
                        password=creds.etdDb.password,
                        host=creds.etdDb.server,
                        database=creds.etdDb.database,
                        port=creds.etdDb.port)
        self.cursor = self.cnxn.cursor()


    def createDbs(self):
        print("Let's create db and init it as needed ")
        for file in self.allSqlFiles:
            x = self.sqlpath + file
            y = open(x,'r').read()
            self.cursor.execute(y)
            print(y)
        self.cursor.close()

    
    def populateCampuses(self):
        print("populate campuses")
        params = []
        with open(self.datapath +'campuses.txt', newline='') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                print(row)
                code = row[0].strip()
                location = row[1].strip()
                pqcode = row[2].strip()
                namesuffix = row[3].strip()
                unit = row[4].strip()
                collection = row[5].strip()
                nameinmarc = code.upper()
                if nameinmarc == 'UCSC':
                    nameinmarc = "University of California, " + namesuffix
                params.append((code,location, pqcode,namesuffix,unit,collection, nameinmarc))
        self.cursor.executemany(self.InsertCampus, params)
        self.cnxn.commit()

    def populateGatewayConfig(self):
        print("populate GatewayConfig")
        params = []
        #with open(self.datapath +'pqmarc_map.txt', newline='') as f:
        with open(self.datapath +'gateway_map.txt', newline='') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                print(row)
                tag = row[0].strip()
                field = row[1].strip()
                attrname = row[2].strip()
                isMultiple = row[3].strip()
                params.append(('Gateway',tag,field,attrname,isMultiple,))
        self.cursor.executemany(self.InsertMarcIn, params)
        self.cnxn.commit()

    def populateSilsConfig(self):
        print("populate SilsConfig")
        params = []
        with open(self.datapath +'silsmarc_map.txt', newline='') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                print(row)
                tag = row[0].strip()
                ind1 = row[1].strip()
                ind2 = row[2].strip()
                field = row[3].strip()
                sourcefield = row[4].strip()
                # if the info field contains '#' then replace with space
                info = row[5].strip().replace('#',' ')
                actionfield = row[6].strip()
                params.append(('MarcOut',tag,ind1,ind2,field,sourcefield,actionfield,info,))
        self.cursor.executemany(self.InsertSilsMap, params)
        self.cnxn.commit()

    def populateEscholConfig(self):
        print("populate EscholConfig")
        params = []
        with open(self.datapath +'eschol_map.txt', newline='') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                print(row)
                field = row[0].strip()
                sourcefield = row[1].strip()
                info = row[2].strip()               
                params.append(('EscholOut',field,sourcefield,info,))
        self.cursor.executemany(self.InsertEscholMap, params)
        self.cnxn.commit()

print("start")
x = configDb()
#x.createDbs()
#x.populateCampuses()
#x.populateGatewayConfig()
x.populateSilsConfig()
#x.populateEscholConfig()
print("end")