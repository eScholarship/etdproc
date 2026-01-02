import consts
import paramiko
import traceback
from datetime import date
from pymarc import MARCReader, MARCWriter


# ============================================================
# Class Name: uploadToOCLCftp
# Description:
#     Uploads consolidated MARC file to OCLC.
#
# Attributes:
#     packageIds ([]): Ids of the ETD in packages table.
#
#
# Usage:
#     x = uploadToOCLCftp(packageId)
#     x._countSent: tells the user count sent 
#
# Notes:
#     - The logic ensures no duplicated record is sent so it 
#     looks at queuelogs to find out if ETD has already been sent to OCLC
# ============================================================
class uploadToOCLCftp:
    _countSent = 0
    _packageIds = None
    _combinedPath = None
    _combinedName = None
    _combinedIds = []
    def __init__(self, packageIds):
        self._countSent = 0
        self._combinedIds = []
        self._packageIds = packageIds
        self.connectAndUpload()
        self._countSent = len(self._combinedIds)

    ########################################
    #
    # Combines records and sends consolidated file
    #
    ########################################
    def connectAndUpload(self):
        if len(self._packageIds) < 1:
            return
        with paramiko.Transport((consts.configs['oclc_creds.host'],int(consts.configs['oclc_creds.port']))) as transport:
            transport.connect(None, consts.configs['oclc_creds.username'], consts.configs['oclc_creds.key'])
            with paramiko.SFTPClient.from_transport(transport) as sftp:
                self.combineMrcFiles()
                self.uploadFiles(sftp)
        return
        

    ########################################
    #
    # Creates consolidated MARC file
    #
    ########################################
    def combineMrcFiles(self):
        # Get today's date in YYYYMMDD format
        today_str = date.today().strftime('%Y%m%d')
        self._combinedName = f'combined_{today_str}.mrc'
        self._combinedPath = f'{consts.marcDir}/{self._combinedName}'
        # Create a FileWriter for the output
        with open(self._combinedPath, 'wb') as out_fh:
            writer = MARCWriter(out_fh)
            for packageid in self._packageIds:
                if consts.db.IsOclcsenddone(packageid):
                    print(f'Skipping OCLC FTP for package id {packageid}')
                    consts.db.saveQueueStatus(packageid, "done")
                    continue
                else:
                    mrcname = consts.db.getMarcName(packageid)
                    assert(mrcname)
                    inpath = f'{consts.marcDir}/{mrcname}'
                    with open(inpath, 'rb') as in_fh:
                        reader = MARCReader(in_fh, to_unicode=True, force_utf8=True, utf8_handling='replace')
                        for record in reader:
                            if record:
                               writer.write(record)
                    self._combinedIds.append(packageid)
            writer.close()

    ########################################
    #
    # Copies file to OCLC
    #
    ########################################
    def uploadFiles(self, sftp):
        sftp.chdir(consts.configs['oclc_creds.uploaddir']) 
        try:
            outpath = f"{consts.configs['oclc_creds.uploaddir']}/{consts.configs['oclc_creds.nameprefix']}{self._combinedName}" 
            print(f'Sending combined file to {outpath}')
            sftp.put(self._combinedPath, outpath)
            for packageid in self._combinedIds:
                consts.db.saveQueueStatus(packageid, "done")
                consts.db.saveQueueLog(packageid, "sils") 
        except Exception as e:
            callstack = traceback.format_exc()
            print(callstack)
            print(e)
            for packageid in self._combinedIds:
                consts.db.saveQueueStatus(packageid, "sils-error") 




########################################
#
# Test for OCLC connection
#
########################################
class uploadToFTP:
    _packageId = None
    _pubnum = None
    _filepath = None
    def __init__(self, packageId):
        print("get the file to upload")
        self._packageId = packageId
        self._pubnum = consts.db.getPubNumber(packageId)
        self._filepath = f'{consts.marcDir}/ETDS-{self._pubnum}.mrc'

    def testConnection(self):
        print("test connection to the OCLC ftp")
        with paramiko.Transport((consts.configs['oclc_creds.host'],int(consts.configs['oclc_creds.port']))) as transport:
            transport.connect(None, consts.configs['oclc_creds.username'], consts.configs['oclc_creds.key'])
            print("got sftp connection")
            #self.testListDir(transport)
            self.testUploadFiles(transport)

    def testListDir(self, transport):
        print("test list directory")
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            self.filesFound = sftp.listdir(consts.configs['oclc_creds.uploaddir'])
            print(self.filesFound)
            for filename in self.filesFound:
                print(filename)

        return

    def testUploadFiles(self, transport):
        print("test upload files")
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            sftp.chdir(consts.configs['oclc_creds.uploaddir'])
            # update filename
            root = "C:/Temp/OCLC/"
            files = ["ETDS-30492756.mrc","ETDS-31847224.mrc","ETDS-31845828.mrc"]
            for file in files:
                outpath = f"{consts.configs['oclc_creds.uploaddir']}/{consts.configs['oclc_creds.nameprefix']}{file}"
                print(outpath)
                sftp.put(root+file, outpath)

        return


#x = uploadToFTP(2)
#x.testConnection()
