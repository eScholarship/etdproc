import consts
import paramiko
from creds import oclc_creds

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
        with paramiko.Transport((oclc_creds.host,oclc_creds.port)) as transport:
            transport.connect(None, oclc_creds.username, oclc_creds.key)
            print("got sftp connection")
            self.testListDir(transport)

    def testListDir(self, transport):
        print("test list directory")
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            self.filesFound = sftp.listdir(oclc_creds.uploaddir)
            print(self.filesFound)
            # what we want to do is put action
            #sftp.put(self._filepath)
            for filename in self.filesFound:
                print(filename)

        return


x = uploadToFTP(2)
x.testConnection()