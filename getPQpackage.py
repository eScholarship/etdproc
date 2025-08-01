import os
import json
import consts
import paramiko
import zipfile
import shutil
from creds import sftp_creds, ucla_creds

class pqSfptIntf:
    filesFound = []
    filesUnziped = []
    def __init__(self):
        self.filesFound = []
        self.filesUnziped = {}

    def getPqPackages(self):
        pkey = paramiko.RSAKey.from_private_key_file("/apps/eschol/.ssh/id_rsa")
        with paramiko.Transport((sftp_creds.host,sftp_creds.port)) as transport:
            transport.connect(None, sftp_creds.username, pkey=pkey)
            print("got sftp connection with proquest")
            return self.getFilesAndUnzip(transport, sftp_creds.directory)

        with paramiko.Transport((ucla_creds.host,ucla_creds.port)) as transport:
            transport.connect(None, ucla_creds.username, pkey=pkey)
            print("got sftp connection uclaetd")
            return self.getFilesAndUnzip(transport, ucla_creds.directory)


    def getFilesAndUnzip(self, transport, directory):      
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            self.filesFound = sftp.listdir(directory)
            print(self.filesFound)
            for filename in self.filesFound:
                # if the zipname is present in DB, skip for now
                local_path = os.path.join(consts.downloadDir, filename)
                remote_path = os.path.join(directory, filename)
                zipname = os.path.splitext(filename)[0]
                if consts.db.IsZipFilePresent(zipname):
                    print(f'Skipping {zipname}')
                    continue
                sftp.get(remote_path, local_path)
                sftp.remove(remote_path)

                # if the file exists in done folder, remove it 
                if self.unzipFile(local_path):
                    dest_folder = consts.doneDir
                else:
                    dest_folder = consts.errorDir

                dest_file = os.path.join(dest_folder, filename)
                if os.path.exists(dest_file):
                    os.remove(dest_file)
                shutil.move(local_path, consts.doneDir)
        return

    def isValidZip(self, zfiles):
        count_proquest = 0
        count_pdf = 0
        for name in zfiles.namelist():
            if name[-9:] == "_DATA.xml":
                print(name)
                count_proquest += 1
            if str(name).endswith(".pdf"):
                print(name)
                count_pdf += 1

        # make sure there is one data file
        # make sure there is a pdf
        return (count_proquest == 1) and (count_pdf > 0)

    def getfileAttrs(self, zfiles, extractfolder):
        xmlname = None
        pdfname = None
        otherfiles = []
        for name in zfiles.namelist():
            if name[-9:] == "_DATA.xml":
                # name is proQuest xml
                xmlname = name
            else:
                otherfiles.append(os.path.basename(name))

        pdfname = xmlname[:-9] + ".pdf"
        if pdfname not in otherfiles:
            # throw
            print("main file not as expected")
        otherfiles.remove(pdfname)

        fileattrs = {"xmlfile": xmlname, "pdffile": pdfname, "supp": otherfiles, "folder": extractfolder}
        return fileattrs

        

    def unzipFile(self, filepath):
        zipname = os.path.splitext(os.path.basename(filepath))[0]
        print("unzip the file and save the files in a new folder")
        if(zipfile.is_zipfile(filepath) == False):
            print(f'{filepath} is not a zip file')
            return False
        with zipfile.ZipFile(filepath, 'r') as zfiles:
            # inspect the zip file
            # make sure it has _DATA file
            if(self.isValidZip(zfiles)):
                zipname = os.path.splitext(os.path.basename(filepath))[0]
                extractfolder = os.path.join(consts.extractDir, zipname)
                zfiles.extractall(extractfolder)
                self.filesUnziped[zipname] = self.getfileAttrs(zfiles, zipname)
                return True
            else:
                print(f'{filepath} is not a valid ProQuest package')
        return False

    def getFullPathForProQuestXml(self, zipname):
        fileatts = self.filesUnziped[zipname]
        # get the xml name
        return os.path.join(consts.extractDir, zipname, fileatts["xmlfile"])

    def saveToDb(self, zipname, packageId):
        print("save fileattrs and create queue item for this")
        fileatts = self.filesUnziped[zipname]
        isparseError = False
        # update fileattr 
        if packageId is None:
            isparseError = True
            # temp pub num and campus for parse-error case
            pubnum = zipname[-20:]
            consts.db.savePackage(pubnum, zipname, 1)
            packageId = consts.db.getPackageId(pubnum)
            
        consts.db.savefileattrs(packageId, json.dumps(fileatts,ensure_ascii=False))
        consts.db.saveQueue(packageId)
        if isparseError:
            consts.db.saveQueueStatus(packageId, "parse-error")

        return packageId
#a = pqSfptIntf()
#a.getStagedFiles()

