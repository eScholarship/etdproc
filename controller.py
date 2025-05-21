
from getPQpackage import pqSfptIntf
from parseXml import etdParseXml
from computeValues import etdcomputeValues
from sendToMerritt import etdToMerritt, marcToMerritt
from parseGateway import etdParseGateway
from depositToEschol import mintEscholId, depositToEschol
from generateMarc import createMarc
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

        if "gw" in queuedtasks:
            self.processGatewayPending(queuedtasks["gw"])

        if "mint" in queuedtasks:
            self.processMintPending(queuedtasks["mint"])

        if "eschol" in queuedtasks:
            self.processEscholDeposit(queuedtasks["eschol"])

        if "sils" in queuedtasks:
            self.processSilsDesposit(queuedtasks["sils"])
        return

    def processSilsDesposit(self, packageIds):
        print("process sils submission")
        for packageid in packageIds:
            x = createMarc(packageid)
            # drop and create DBs and add seed data
            marcfile = x.writeMarcFile()
            # x._compAttrs["merrittark"]
            y = marcToMerritt(marcfile, x._compAttrs["merrittark"])
            y.sendToMerritt()
            # need to send the generated marc file to Merritt
            # find out information about FTP for SILS
            consts.db.saveQueueStatus(packageid, "done")

    def processMintPending(self, packageIds):
        print("process mint requests")
        for packageid in packageIds:
            x = mintEscholId(packageid)
            x.mint()
            consts.db.saveQueueStatus(packageid, "eschol")


    def processEscholDeposit(self, packageIds):
        print("process eschol deposits")
        for packageid in packageIds:
            x = depositToEschol(packageid)
            x.deposit()
            consts.db.saveQueueStatus(packageid, "sils")


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
        queuedMC = consts.db.getUnprocessedMCs()
        for mcid in queuedMC:
            # extract pub number from json and if the stutus is COMPLETED then move the queue status to gw
            data = json.loads(queuedMC[mcid])
            jobstatus = data["job:jobState"]["job:jobStatus"].lower()
            pubnum = data["job:jobState"]["job:localID"]
            packageid = consts.db.getPackageId(pubnum)
            if jobstatus == "completed":
                merrittark = data["job:jobState"]["job:primaryID"]
                consts.db.saveMerrittArk(packageid, merrittark)
                # advance queue status
                consts.db.saveQueueStatus(packageid, "gw")
            else:
                consts.db.saveQueueStatus(packageid, "merritt-error")
            consts.db.markMCprocessed(mcid)

        # also get merrittark and update that entry
        # if status is QUEUED - leave status as it is
        
    def processGatewayPending(self, packageIds):
        print("find all package pending information from gw")
        print(packageIds)
        # extract these
        for packageid in packageIds:
            print("package waiting for data from Gateway")
            x = etdParseGateway(packageid)
            if x.process():
                consts.db.saveQueueStatus(packageid, "mint")

# add to DB and create a queue entry

# process items in fetch state for the package
# get items in fetch state for next state of processing





# fetch - maybe unzip to htdoc for serving purposes
# parsexml, fetcherror
c = Controller()
#c.buildQueue()
c.processQueue()
#c.processMerrittCallbacks()