import paramiko
import zipfile
from creds import sftp
from datetime import datetime
import os

class pqSfptIntf:
    downloadDir = '/apps/eschol/etdproc/zip/download'
    extractDir = '/apps/eschol/etdproc/zip/extract'
    doneDir = '/apps/eschol/etdproc/zip/done'
    errorDir = '/apps/eschol/etdproc/zip/error'
    def __init__(self):
        print("created intf")
        print("connecting")
        self.transport = paramiko.Transport((sftp.host,sftp.port))
        # get staged files
        #self.getStagedFiles()
        # look over the files and process those

    def getStagedFiles(self):
        self.filesFound = []
        pkey = paramiko.RSAKey.from_private_key_file("/apps/eschol/.ssh/id_rsa")
        self.transport.connect(None,sftp.username, pkey=pkey)
        print("got sftp connection")
        with paramiko.SFTPClient.from_transport(self.transport) as sftp:
            filesFound = sftp.listdir(sftp.username)
            print(filesFound)
            for filename in filesFound:
                local_path = os.path.join(self.downloadDir, filename)
                remote_path = os.path.join(sftp.username, filename)
                sftp.get(remote_path, local_path)
                # tbd - remove the file from sftp site
                #sftp.remove(remote_file_path)
                self.unzipFile(local_path)

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

        assert(zipfile.is_zipfile(filepath))
        zfiles = zipfile.ZipFile(filepath, 'r')

        # inspect the zip file
        # make sure it has _DATA file
        assert(self.isValidZip(zfiles))
        zfiles.extractall(self.extractDir)

a = pqSfptIntf()
a.getStagedFiles()

