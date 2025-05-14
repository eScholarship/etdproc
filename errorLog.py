from dbIntf import etdDb
db = etdDb()

class CustomError(Exception):
    def __init__(self, message, details):
        super().__init__(message)
        self.details = details
        self.message = message 

    def saveLog(self,packageId):
        print("save info in DB")
        #TBD
        #db.saveError(packageId, self.message, self.details)
