import consts
import traceback
from parseXml import reparseXml
from generateMarc import createMarc
from parseGateway import etdParseGateway
from computeValues import etdcomputeValues
from sendToMerritt import etdToMerritt, marcToMerritt
from depositToEschol import mintEscholId, depositToEschol, replaceEscholMetadata


class processQueueImpl:
    _fetchedTasks = []
    _extractedTasks = []
    _gatewayTasks = []
    _mintTasks = []
    _escholTasks = []
    _marcTasks = []
    _silsTasks = []
    def __init__(self):
        print("process queues")
        self._fetchedTasks = []
        self._extractedTasks = []
        self._gatewayTasks = []
        self._mintTasks = []
        self._escholTasks = []
        self._marcTasks = []
        self._silsTasks = []
        self._reparseTasks = []
        self._recompTasks = []
        self._remetaTasks = []
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

        if "marc" in queuedtasks:
            self._marcTasks = queuedtasks["marc"]

        if "sils" in queuedtasks:
            self._silsTasks = queuedtasks["sils"]

        if "reparse" in queuedtasks:
            self._reparseTasks = queuedtasks["reparse"]

        if "recomp" in queuedtasks:
            self._recompTasks = queuedtasks["recomp"]

        if "remeta" in queuedtasks:
            self._remetaTasks = queuedtasks["remeta"]


    def processQueue(self):
        print("query to find items with specific status")
        # get all the items where status is not done
        self.processFetched()
        self.processExtracted()
        self.processGatewayPending()
        self.processMintPending()
        self.processEscholDeposit()
        self.processMarcGeneration()
        self.processSilsDesposit()

        self.processReparse()
        self.processRecomp()
        self.processRemeta()

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
                callstack = traceback.format_exc()
                print(callstack)
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
                callstack = traceback.format_exc()
                print(callstack)
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
                callstack = traceback.format_exc()
                print(callstack)
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
                callstack = traceback.format_exc()
                print(callstack)
                print(e)
                consts.db.saveQueueStatus(packageid, "mint-error") 

    def processEscholDeposit(self):
        print("process eschol deposits")
        for packageid in self._escholTasks:
            try:
                x = depositToEschol(packageid)
                x.deposit()
                consts.db.saveQueueStatus(packageid, "marc")
                self._marcTasks.append(packageid)
            except Exception as e:
                callstack = traceback.format_exc()
                print(callstack)
                print(e)
                consts.db.saveQueueStatus(packageid, "eschol-error") 

    def processMarcGeneration(self):
        print("generate marc records")
        for packageid in self._marcTasks:
            try:
                x = createMarc(packageid)
                marcfile = x.writeMarcFile()
                y = marcToMerritt(marcfile, x._compattrs["merrittark"])
                y.sendToMerritt()
                consts.db.saveQueueStatus(packageid, "sils")
                self._silsTasks.append(packageid)
            except Exception as e:
                callstack = traceback.format_exc()
                print(callstack)
                print(e)
                consts.db.saveQueueStatus(packageid, "marc-error") 

    def processSilsDesposit(self):
        print("process sils submission")
        for packageid in self._silsTasks:
            try:
                # TBD to ftp for OCLC
                consts.db.saveQueueStatus(packageid, "done")
            except Exception as e:
                callstack = traceback.format_exc()
                print(callstack)
                print(e)
                consts.db.saveQueueStatus(packageid, "sils-error") 

    def processReparse(self):
        print("process reparse xml")
        for packageid in self._reparseTasks:
            try:
                a = reparseXml(packageid)
                a.convertAndSave()
                consts.db.saveQueueStatus(packageid, "recomp")
                self._recompTasks.append(packageid)
            except Exception as e:
                callstack = traceback.format_exc()
                print(callstack)
                print(e)
                consts.db.saveQueueStatus(packageid, "reparse-error") 

    def processRecomp(self):
        print("process recompute values")
        for packageid in self._recompTasks:
            try:
                x = etdcomputeValues(packageid)
                x.saveComputedValues()
                isMerrittArk = False
                if "merrittark" in x._compAttrs:
                    if "ark:" in x._compAttrs["merrittark"]:
                        isMerrittArk = True
                if consts.db.IsDeposited(packageid):
                    consts.db.saveQueueStatus(packageid, "remeta")
                    self._remetaTasks.append(packageid)
                elif isMerrittArk:
                    consts.db.saveQueueStatus(packageid, "gw")
                else:
                    consts.db.saveQueueStatus(packageid, "extract")
            except Exception as e:
                callstack = traceback.format_exc()
                print(callstack)
                print(e)
                consts.db.saveQueueStatus(packageid, "recomp-error") 

    def processRemeta(self):
        print("process replace metadata")
        for packageid in self._remetaTasks:
            try:
                x = replaceEscholMetadata(packageid)
                x.replaceMeta()
                consts.db.saveQueueStatus(packageid, "done")
            except Exception as e:
                callstack = traceback.format_exc()
                print(callstack)
                print(e)
                consts.db.saveQueueStatus(packageid, "remeta-error") 

