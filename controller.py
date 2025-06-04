
import os
import json
import consts
from getPQpackage import pqSfptIntf
from parseXml import etdParseXml
from processQueues import processQueueImpl


class Controller:
    def __init__(self):
        print("starting controller")
        self.buildQueue()
        self.processMerrittCallbacks()
        x = processQueueImpl() 
        x.processQueue()

    def buildQueue(self):
        print("bring in files from ")
        #zippath = "C:/Users/myucekul/Downloads/etdadmin_upload_1139353.zip"
        zippath = os.path.join(consts.downloadDir, "etdadmin_upload_1140749.zip")
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


    def processMerrittCallbacks(self):
        # find out unprocess entries from callback table
        queuedMC = consts.db.getUnprocessedMCs()
        for mcid in queuedMC:
            # extract pub number from json and if the stutus is COMPLETED then move the queue status to gw
            data = json.loads(queuedMC[mcid])
            jobstatus = data["job:jobState"]["job:jobStatus"].lower()
            pubnum = data["job:jobState"]["job:localID"]
            packageid = consts.db.getPackageId(pubnum)
            isForInitialSubmission = data["job:jobState"]["job:packageName"].endswith(".zip")
            if isForInitialSubmission:
                if jobstatus == "completed":
                    merrittark = data["job:jobState"]["job:primaryID"]
                    consts.db.saveMerrittArk(packageid, merrittark)
                    # advance queue status
                    consts.db.saveQueueStatus(packageid, "gw")
                else:
                    consts.db.saveQueueStatus(packageid, "merritt-error")
            else:
                print("This is for addition to existing ETD")
            consts.db.markMCprocessed(mcid)

        # also get merrittark and update that entry
        # if status is QUEUED - leave status as it is
        


# add to DB and create a queue entry

# process items in fetch state for the package
# get items in fetch state for next state of processing





# fetch - maybe unzip to htdoc for serving purposes
# parsexml, fetcherror
c = Controller()
#c.buildQueue()
#c.processQueue()
#c.processMerrittCallbacks()