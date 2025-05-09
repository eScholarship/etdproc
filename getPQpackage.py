import paramiko
import zipfile
from creds import sftp_creds
from datetime import datetime
import os

class pqSfptIntf:
    downloadDir = '/apps/eschol/etdproc/zip/download'
    extractDir = '/apps/eschol/etdproc/zip/extract'
    doneDir = '/apps/eschol/etdproc/zip/done'
    errorDir = '/apps/eschol/etdproc/zip/error'
    filesFound = []
    filesUnziped = []
    def __init__(self):
        print("created intf")
        print("connecting")
        self.filesFound = []
        self.filesUnziped = []
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
                local_path = os.path.join(self.downloadDir, filename)
                remote_path = os.path.join(sftp_creds.username, filename)
                sftp.get(remote_path, local_path)
                # tbd - remove the file from sftp site
                #sftp.remove(remote_file_path)
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

    def unzipFile(self, filepath):
        print("unzip the file and save the files in a new folder")
        if(zipfile.is_zipfile(filepath) == False):
            print(f'{filepath} is not a zip file')
            return
        zfiles = zipfile.ZipFile(filepath, 'r')
        # inspect the zip file
        # make sure it has _DATA file
        if(self.isValidZip(zfiles)):
            zfiles.extractall(self.extractDir)
            self.filesUnziped.append(filepath)
        else:
            print(f'{filepath} is not a valid ProQuest package')
        return

a = pqSfptIntf()
a.getStagedFiles()

