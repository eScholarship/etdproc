import consts
import traceback
from parseXml import reparseXml
from generateMarc import createMarc
from sendToSILS import uploadToOCLCftp
from parseGateway import etdParseGateway
from computeValues import etdcomputeValues
from oaiupdate import OaiUpdate
from sendToMerritt import etdToMerritt, marcToMerritt
from depositToEschol import mintEscholId, depositToEschol, replaceEscholMetadata

# ============================================================
# This is the main class that goes through queued ETD items and processes
# ============================================================
class processQueueImpl:
    _fetchedTasks = []
    _extractedTasks = []
    _gatewayTasks = []
    _mintTasks = []
    _escholTasks = []
    _marcTasks = []
    _silsTasks = []
    _reparseTasks = []
    _recompTasks = []
    _remetaTasks = []
    _oaiupdateTasks = []
    def __init__(self):
        print("process queues")
        self._fetchedTasks = []
        self._parseTasks = []
        self._extractedTasks = []
        self._gatewayTasks = []
        self._mintTasks = []
        self._escholTasks = []
        self._marcTasks = []
        self._silsTasks = []
        self._reparseTasks = []
        self._recompTasks = []
        self._remetaTasks = []
        self._oaiupdateTasks = []
        self.fillTasks()

    def fillTasks(self):
        print("prepare the queues")
        queuedtasks = consts.db.getAllQueuedTasks()

        if "parse" in queuedtasks:
            self._parseTasks = queuedtasks["parse"]

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

        if "oaiupdate" in queuedtasks:
            self._oaiupdateTasks = queuedtasks["oaiupdate"]

    def processQueue(self):
        print("query to find items with specific status")
        # get all the items where status is not done
        self.processParse()
        self.processFetched()
        self.processExtracted()
        self.processGatewayPending()
        self.processMintPending()
        self.processEscholDeposit()
        self.processMarcGeneration()
        self.processSilsDesposit()

        self.processOaiUpdate()
        self.processReparse()
        self.processRecomp()
        self.processRemeta()

        return

    def processParse(self):
        # extract these
        for packageid in self._parseTasks:
            try:
                consts.db.saveQueueLog(packageid, "parse") 
                a = reparseXml(packageid)
                a.convertAndSave()
                # update queue item status
                consts.db.saveQueueStatus(packageid, "fetch")
                self._fetchedTasks.append(packageid)
            except Exception as e:
                callstack = traceback.format_exc()
                print(callstack)
                print(e)
                consts.db.saveQueueStatus(packageid, "parse-error")
            # TBD - error case

    def processFetched(self):
        # extract these
        for packageid in self._fetchedTasks:
            try:
                consts.db.saveQueueLog(packageid, "fetch") 
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
                consts.db.saveQueueLog(packageid, "extract") 
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
                consts.db.saveQueueLog(packageid, "gw") 
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
                consts.db.saveQueueLog(packageid, "mint") 
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
                consts.db.saveQueueLog(packageid, "eschol") 
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
                consts.db.saveQueueLog(packageid, "marc") 
                x = createMarc(packageid)
                marcfile = x.writeMarcFile()
                y = marcToMerritt(x._compattrs["merrittark"], x._compattrs["merrittbucket"])
                y.sendFileToMerritt(marcfile)
                consts.db.saveQueueStatus(packageid, "sils")
                self._silsTasks.append(packageid)
            except Exception as e:
                callstack = traceback.format_exc()
                print(callstack)
                print(e)
                consts.db.saveQueueStatus(packageid, "marc-error") 

    def processSilsDesposit(self):
        print("process sils submission")
        if consts.configs['oclc_creds.sentToOclc'] != 'True':
            for packageid in self._silsTasks:
                consts.db.saveQueueStatus(packageid, "done")
        else:
            x = uploadToOCLCftp(self._silsTasks)
            print(f'Sent {x._countSent} files to OCLC')

    def processReparse(self):
        print("process reparse xml")
        for packageid in self._reparseTasks:
            try:
                consts.db.saveQueueLog(packageid, "reparse") 
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
                consts.db.saveQueueLog(packageid, "recomp") 
                x = etdcomputeValues(packageid)
                x.saveComputedValues()
                isMerrittArk = False
                if "merrittark" in x._compAttrs:
                    if "ark:" in x._compAttrs["merrittark"]:
                        isMerrittArk = True
                # updating to remeta to marc stage for now
                if consts.db.IsDeposited(packageid):
                    consts.db.saveQueueStatus(packageid, "marc")
                    #self._remetaTasks.append(packageid)
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
                consts.db.saveQueueLog(packageid, "remeta") 
                x = replaceEscholMetadata(packageid)
                x.replaceMeta()
                consts.db.saveQueueStatus(packageid, "done")
            except Exception as e:
                callstack = traceback.format_exc()
                print(callstack)
                print(e)
                consts.db.saveQueueStatus(packageid, "remeta-error") 


    def processOaiUpdate(self):
        print("process oai updates")
        for packageid in self._oaiupdateTasks:
            try:
                consts.db.saveQueueLog(packageid, "oaiupdate") 
                x = OaiUpdate(packageid)
                x.process()
                #consts.db.saveQueueStatus(packageid, "done")
            except Exception as e:
                callstack = traceback.format_exc()
                print(callstack)
                print(e)
                consts.db.saveQueueStatus(packageid, "oaiupdate-error") 

