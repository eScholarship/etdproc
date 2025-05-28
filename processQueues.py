import consts
from generateMarc import createMarc
from parseGateway import etdParseGateway
from computeValues import etdcomputeValues
from sendToMerritt import etdToMerritt, marcToMerritt
from depositToEschol import mintEscholId, depositToEschol


class processQueueImpl:
    _fetchedTasks = []
    _extractedTasks = []
    _gatewayTasks = []
    _mintTasks = []
    _escholTasks = []
    _silsTasks = []
    def __init__(self):
        print("process queues")
        self._fetchedTasks = []
        self._extractedTasks = []
        self._gatewayTasks = []
        self._mintTasks = []
        self._escholTasks = []
        self._silsTasks = []
        self.fillTasks()

    def fillTasks(self):
        print("prepare the queues")
        queuedtasks = consts.db.getAllQueuedTasks()
        if "fetch" in queuedtasks:
            self._fetchedTasks = queuedtasks["fetch"]

        if "extract" in queuedtasks:
            self._extractedTasks = queuedtasks["extract"]

        if "gw" in queuedtasks:
            self._gatewayTasks = queuedtasks["gw"]

        if "mint" in queuedtasks:
            self._mintTasks = queuedtasks["mint"]

        if "eschol" in queuedtasks:
            self._escholTasks = queuedtasks["eschol"]

        if "sils" in queuedtasks:
            self._silsTasks = queuedtasks["sils"]

    def processQueue(self):
        print("query to find items with specific status")
        # get all the items where status is not done
        self.processFetched()
        self.processExtracted()
        self.processGatewayPending()
        self.processMintPending()
        self.processEscholDeposit()
        self.processSilsDesposit()

        return

    def processFetched(self):
        # extract these
        for packageid in self._fetchedTasks:
            try:
                x = etdcomputeValues(packageid)
                x.saveComputedValues()
                # update queue item status
                consts.db.saveQueueStatus(packageid, "extract")
                self._extractedTasks.append(packageid)
            except Exception as e:
                print(e)
                consts.db.saveQueueStatus(packageid, "fetch-error")
            # TBD - error case

    def processExtracted(self):
        # extract these
        for packageid in self._extractedTasks:
            try:
                x = etdToMerritt(packageid)
                x.process()
                consts.db.saveQueueStatus(packageid, "merritt")
            except Exception as e:
                print(e)
                consts.db.saveQueueStatus(packageid, "extract-error") 

    def processGatewayPending(self):
        print("find all package pending information from gw")
        # extract these
        for packageid in self._gatewayTasks:
            try:
                x = etdParseGateway(packageid)
                if x.process():
                    consts.db.saveQueueStatus(packageid, "mint")
                    self._mintTasks.append(packageid)
            except Exception as e:
                print(e)
                consts.db.saveQueueStatus(packageid, "gw-error") 

    def processMintPending(self):
        print("process mint requests")
        for packageid in self._mintTasks:
            try:
                x = mintEscholId(packageid)
                x.mint()
                consts.db.saveQueueStatus(packageid, "eschol")
                self._escholTasks.append(packageid)
            except Exception as e:
                print(e)
                consts.db.saveQueueStatus(packageid, "mint-error") 

    def processEscholDeposit(self):
        print("process eschol deposits")
        for packageid in self._escholTasks:
            try:
                x = depositToEschol(packageid)
                x.deposit()
                consts.db.saveQueueStatus(packageid, "sils")
                self._silsTasks.append(packageid)
            except Exception as e:
                print(e)
                consts.db.saveQueueStatus(packageid, "eschol-error") 

    def processSilsDesposit(self):
        print("process sils submission")
        for packageid in self._silsTasks:
            try:
                x = createMarc(packageid)
                # drop and create DBs and add seed data
                marcfile = x.writeMarcFile()
                # x._compAttrs["merrittark"]
                y = marcToMerritt(marcfile, x._compattrs["merrittark"])
                y.sendToMerritt()
                # need to send the generated marc file to Merritt
                # find out information about FTP for SILS
                consts.db.saveQueueStatus(packageid, "done")
            except Exception as e:
                print(e)
                consts.db.saveQueueStatus(packageid, "sils-error") 

