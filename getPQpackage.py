from ftplib import FTP_TLS
import zipfile
from datetime import datetime
import os

class pqSfptIntf:
    remote = 'sftp-stg.cdlib.org'
    section = 'proquest'
    workingDir = '/apps/eschol/etdproc/zip/working'
    doneDir = '/apps/eschol/etdproc/zip/done'
    errorDir = '/apps/eschol/etdproc/zip/error'
    def __init__(self):
        print("created intf")
        # get staged files
        #self.getStagedFiles()
        # look over the files and process

    def getStagedFiles(self):
        self.filesFound = []
        with FTP_TLS(self.remote, self.section ) as ftps:
            ftps.prot_p()
            print(ftps.nlst())
            # use ftplib to get the files on the server
            self.filesFound = ftps.nlst()
            for filename in self.filesFound:
                print(filename)
                local_filename = os.path.join(self.workingDir, filename)
                file = open(local_filename, 'wb')
                ftps.retrbinary('RETR '+ filename, file.write)
                # tbd - remove the file from FTP site
                #ftps.delete(filename)

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

    def unzipFile(self, filepath, extractpath):
        print("unzip the file and save the files in a new folder")

        assert(zipfile.is_zipfile(filepath))
        zfiles = zipfile.ZipFile(filepath, 'r')

        # inspect the zip file
        # make sure it has _DATA file
        assert(self.isValidZip(zfiles))

        zfiles.extractall(extractpath)

a = pqSfptIntf()
a.unzipFile("C:/Temp/test/ark+=13030=m5ch0sz1.zip", "C:/Temp/test")
