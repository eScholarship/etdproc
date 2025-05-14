
from getPQpackage import pqSfptIntf
from parseXml import etdParseXml
import consts

class Controller:
    def __init__(self):
        print("starting controller")
        #self.buildQueue()
        #self.processQueue()

    def buildQueue(self):
        print("bring in files from ")
        zippath = "C:/Users/myucekul/Downloads/etdadmin_upload_1139353.zip"
        # get the packages
        x = pqSfptIntf()
        #x.getPqPackages()
        x.unzipFile(zippath)
        for item in x.filesUnziped:
            xmlpath = x.getFullPathForProQuestXml(item)
            # create entries in DB 
            a = etdParseXml()
            a.convertToJson(xmlpath)
            packageId = a.saveToDb() 

            # add to queue and indicate status fetch
            x.saveToDb(item, packageId)


    def processQueue(self):
        print("query to find items with specific status")
        # get all the items where status is not done
        queuedtasks = consts.db.getAllQueuedTasks()

        if "fetch" in queuedtasks:
            self.processFetched(queuedtasks["fetch"])
        return

    def processFetched(self, packageIds):
        print(packageIds)
        # extract these
# add to DB and create a queue entry

# process items in fetch state for the package
# get items in fetch state for next state of processing





# fetch - maybe unzip to htdoc for serving purposes
# parsexml, fetcherror
c = Controller()
#c.buildQueue()
c.processQueue()