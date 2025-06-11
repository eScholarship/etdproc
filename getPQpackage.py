import paramiko
import zipfile
from creds import sftp_creds
from datetime import datetime
import os
from pathlib import Path
import json
import consts

class pqSfptIntf:
    filesFound = []
    filesUnziped = []
    def __init__(self):
        print("created intf")
        print("connecting")
        self.filesFound = []
        self.filesUnziped = {}
        #self.transport = paramiko.Transport((sftp_creds.host,sftp_creds.port))
        # get staged files
        #self.getStagedFiles()
        # look over the files and process those

    def getPqPackages(self):
        pkey = paramiko.RSAKey.from_private_key_file("/apps/eschol/.ssh/id_rsa")
        with paramiko.Transport((sftp_creds.host,sftp_creds.port)) as transport:
            transport.connect(None, sftp_creds.username, pkey=pkey)
            print("got sftp connection")
            return self.getFilesAndUnzip(transport)


    def getFilesAndUnzip(self, transport):      
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            self.filesFound = sftp.listdir(sftp_creds.username)
            print(self.filesFound)
            for filename in self.filesFound:
                # if the zipname is present in DB, skip for now
                local_path = os.path.join(consts.downloadDir, filename)
                remote_path = os.path.join(sftp_creds.username, filename)
                sftp.get(remote_path, local_path)
                # tbd - remove the file from sftp site
                sftp.remove(remote_path)
                self.unzipFile(local_path)
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
        if consts.db.IsZipFilePresent(zipname):
            print(f'Skipping {zipname}')
            return
        print("unzip the file and save the files in a new folder")
        if(zipfile.is_zipfile(filepath) == False):
            print(f'{filepath} is not a zip file')
            return
        zfiles = zipfile.ZipFile(filepath, 'r')
        # inspect the zip file
        # make sure it has _DATA file
        if(self.isValidZip(zfiles)):
            zipname = os.path.splitext(os.path.basename(filepath))[0]
            extractfolder = os.path.join(consts.extractDir, zipname)
            zfiles.extractall(extractfolder)
            self.filesUnziped[zipname] = self.getfileAttrs(zfiles, zipname)
        else:
            print(f'{filepath} is not a valid ProQuest package')
        return

    def getFullPathForProQuestXml(self, zipname):
        fileatts = self.filesUnziped[zipname]

        # get the xml name
        return os.path.join(consts.extractDir, zipname, fileatts["xmlfile"])
        #for name in names:
        #    if name[-9:] == "_DATA.xml":
        #        # keep this file in extract folder
        #        print(name)
        #    else:
        #        # move rest to deposit folder
        #directory = os.path.join(self.extractDir, zipname) 
        #for root, _, files in os.walk(directory):
        #    for file in files:
        #        relative_path = os.path.relpath(os.path.join(root, file), directory)
        #        #files_list.append(relative_path)

    def saveToDb(self, zipname, packageId):
        print("save fileattrs and create queue item for this")
        fileatts = self.filesUnziped[zipname]
        # update fileattr 
        consts.db.savefileattrs(packageId, json.dumps(fileatts,ensure_ascii=False))
        consts.db.saveQueue(packageId)

#a = pqSfptIntf()
#a.getStagedFiles()

