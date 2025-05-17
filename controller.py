
from getPQpackage import pqSfptIntf
from parseXml import etdParseXml
from computeValues import etdcomputeValues
from sendToMerritt import etdToMerritt
import consts
import os
import json

class Controller:
    def __init__(self):
        print("starting controller")
        #self.buildQueue()
        #self.processQueue()

    def buildQueue(self):
        print("bring in files from ")
        #zippath = "C:/Users/myucekul/Downloads/etdadmin_upload_1139353.zip"
        zippath = os.path.join(consts.downloadDir, "etdadmin_upload_1139353.zip")
        # get the packages
        x = pqSfptIntf()
        #x.getPqPackages()
        x.unzipFile(zippath)
        for item in x.filesUnziped:
            xmlpath = x.getFullPathForProQuestXml(item)
            # create entries in DB 
            a = etdParseXml(item, xmlpath)
            #a.convertToJson(xmlpath)
            packageId = a.saveToDb() 

            # add to queue and indicate status fetch
            x.saveToDb(item, packageId)


    def processQueue(self):
        print("query to find items with specific status")
        # get all the items where status is not done
        queuedtasks = consts.db.getAllQueuedTasks()

        if "fetch" in queuedtasks:
            self.processFetched(queuedtasks["fetch"])

        if "extract" in queuedtasks:
            self.processExtracted(queuedtasks["extract"])

        return

    def processFetched(self, packageIds):
        print(packageIds)
        # extract these
        for packageid in packageIds:
            x = etdcomputeValues(packageid)
            x.saveComputedValues()
            # update queue item status
            consts.db.saveQueueStatus(packageid, "extract")
            # TBD - error case

    def processExtracted(self, packageIds):
        print(packageIds)
        # extract these
        for packageid in packageIds:
            print("package waiting for Merritt upload")
            x = etdToMerritt(packageid)
            x.process()
            consts.db.saveQueueStatus(packageid, "merritt")
            # next look at the callback table to find out if the item was processed 

    def processMerrittCallbacks(self):
        # find out unprocess entries from callback table
        queuedMC = consts.db.getMerrittCallbacks()
        for mc in queuedMC:
        # extract pub number from json and if the stutus is COMPLETED then move the queue status to gw
            data = json.load(mc)
            jobstatus = data["job:jobState"]["job:jobStatus"].lower()
            pubnum = data["job:jobState"]["job:localID"]
            packageId = consts.db.getPackageId(pubnum)
            if jobstatus == "completed":
                merrittark = data["job:jobState"]["job:primaryID"]
                consts.db.saveMerrittArk(packageId, merrittark)
                # advance queue status
                consts.db.saveQueueStatus(packageId, "gw")
                

        # also get merrittark and update that entry
        # if status is QUEUED - leave status as it is
        # if  

# add to DB and create a queue entry

# process items in fetch state for the package
# get items in fetch state for next state of processing





# fetch - maybe unzip to htdoc for serving purposes
# parsexml, fetcherror
c = Controller()
#c.buildQueue()
c.processQueue()