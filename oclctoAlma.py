import os
import creds
import paramiko
from datetime import datetime
from pymarc import MARCReader, XMLWriter, Field

# oclcDir = '/apps/eschol/etdproc/oclc/in/'
# almaDir = '/apps/eschol/etdproc/oclc/out/'
oclcDir = './out/in/'
almaDir = './out/out/'

class connectAlma:
    key_path = None
    private_key = None
    _fileset = []
    def __init__(self, fileset):
        # Path to your private key file (e.g., id_rsa)
        self.key_path = "./appdata/AlmaNZftp_rsa.txt"
        self._fileset = fileset
        # Load the private key
        self.private_key = paramiko.RSAKey.from_private_key_file(self.key_path)

    def process(self):
        print("test connection to the ALMA ftp")
        with paramiko.Transport((creds.alma_creds.host,creds.alma_creds.port)) as transport:
            transport.connect(username=creds.alma_creds.username, pkey=self.private_key)
            print("got sftp connection")
            self.upload(transport)



    def upload(self, transport):
        print("test list directory")
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            for filename in self._fileset:
                print(f'uploading {filename}')
                local_path = os.path.join(almaDir, filename)
                remote_path = f"{creds.alma_creds.directory}/{filename}"
                #sftp.put(local_path, remote_path)

class connectOCLC:
    _localdir = './out/in'
    _fromdate = None
    def __init__(self):
        print("get the file to upload")
        self._fromdate = datetime.strptime(creds.oclc_creds.downloadfromdate, "%Y-%m-%d")


    def fetch(self):
        print("test connection to the OCLC ftp")
        with paramiko.Transport((creds.oclc_creds.host,creds.oclc_creds.port)) as transport:
            transport.connect(None, creds.oclc_creds.username, creds.oclc_creds.key)
            print("got sftp connection")
            self.processfetch(transport)
            #self.testUploadFiles(transport)


    def processfetch(self, transport):
        print("test list directory")
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            for attr in sftp.listdir_attr(creds.oclc_creds.downloadfolder):
                if(attr.filename.endswith(creds.oclc_creds.namesuffix)):
                    self.downloadFile(sftp, attr)
                      
        return

    def downloadFile(self, sftp, attr):
        modified_time = datetime.fromtimestamp(attr.st_mtime)
        if modified_time > self._fromdate:
            remote_path = os.path.join(creds.oclc_creds.downloadfolder, attr.filename)
            local_path = os.path.join(self._localdir, attr.filename)
            print(attr.filename, "last modified:", modified_time)
            sftp.get(remote_path, local_path)

class recalculateLength:
    _fileForUpload = []
    def __init__(self):
        print("starting")
        self._fileForUpload = []

    def process(self):
        for filename in os.listdir(oclcDir):
            in_path = os.path.join(oclcDir, filename)
            filename_xml = filename.replace(".mrc", ".xml")
            out_path = os.path.join(almaDir, filename_xml)
            print(f"Reading: {filename}")
            self.writeFile(in_path, out_path)
            self._fileForUpload.append(filename_xml)

        return self._fileForUpload

    def writeFile(self, file_path, out_path):
        with open(out_path, 'wb') as out_fh:
            writer = XMLWriter(out_fh)
            
            with open(file_path, 'rb') as fh:
                reader = MARCReader(fh)
                for record in reader:
                    if record:
                        record.force_utf8 = True
                        writer.write(record)
            writer.close()

print("start")  
# get the files from OCLC
# x = connectOCLC()
# x.fetch()
x = recalculateLength()
fileset = x.process()
if len(fileset):
    y = connectAlma(fileset)
    y.process()
# x = connectAlma()
# x.testConnection()
# Resave the record

# save the file in another ftp

print("end")