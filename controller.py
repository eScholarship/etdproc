import os
import shutil
import json
import consts
import traceback
from getPQpackage import pqSfptIntf
from parseXml import etdParseXml
from processQueues import processQueueImpl
from harvestMarc import harvertMarc
from processOai import processOai

class Controller:
    def __init__(self):
        print("starting controller")
        self.buildQueue()
        self.processMerrittCallbacks()
        self.OaiHarvest()
        x = processQueueImpl() 
        x.processQueue()

    def buildQueue(self):
        print("bring in files from ")
        x = pqSfptIntf()
        x.getPqPackages()
        for item in x.filesUnziped:
            try:
                xmlpath = x.getFullPathForProQuestXml(item)
                # create entries in DB 
                a = etdParseXml(item, xmlpath, None)
                #a.convertToJson(xmlpath)
                packageId = a.saveToDb() 

                # add to queue and indicate status fetch
                x.saveToDb(item, packageId)
            except Exception as e:
                callstack = traceback.format_exc()
                print(callstack)
                print(e)
                packageId = x.saveToDb(item, None)
                consts.db.saveErrorLog(packageId,"parse and save operation failed", item)
        return


    def getpubnumFromMC(self, localId, isInitSub):
        pubnum = localId
        # the local id may be a combination of pubnum and date from mrc such as 31844343;ucla.etd:PQ23750
        if "ucla" in localId:
            pubnum = localId.split(';')[0]
        
        # remove prefix to get the number
        if ':' in pubnum:
            pubnum = pubnum.split(':')[1]
        packageid = consts.db.getPackageId(pubnum)

        return packageid

    def processMerrittCallbacks(self):
        # find out unprocess entries from callback table
        queuedMC = consts.db.getUnprocessedMCs()
        for mcid in queuedMC:
            # extract pub number from json and if the stutus is COMPLETED then move the queue status to gw
            packageid = None
            data = json.loads(queuedMC[mcid])
            jobstatus = data["job:jobState"]["job:jobStatus"].lower()                       
            isForInitialSubmission = data["job:jobState"]["job:packageName"].endswith(".zip")
            # found a case when local id was not included in callback package for submission after the initial one
            # no need to process those since merritt id is retrived from the initial submission callback
            if "job:localID" in data["job:jobState"]:
                packageid = self.getpubnumFromMC(str(data["job:jobState"]["job:localID"]), isForInitialSubmission)
            if isForInitialSubmission and packageid:
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

    def OaiHarvest(self):
        print("run OAI harvest")
        x = harvertMarc()
        x.getFeedAndSave()
        print("process OAI harvest")
        y = processOai()
        y.parseMarcInfo()

    def purgeExtracted(self):
        print("purging old")
        folders = consts.db.getDoneFolders()
        for folder in folders:
            dir_path = os.path.join(consts.extractDir, folder)
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    print(f"Deleted: {dir_path}")
                except Exception as e:
                    print(f"Failed to delete {dir_path}: {e}")
        
# Create the controller to build queue and process all
c = Controller()
c.purgeExtracted()

