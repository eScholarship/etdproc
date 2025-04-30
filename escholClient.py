import creds
import requests
import json

########################################
#
# Interfaces with escholarship graphQL 
#
########################################
class graphClient:
    def __init__(self, ep):
        self.endpoint = ep
        self.headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'Privileged':creds.eschol.privKey
                   }
        if creds.eschol.cookie:
            self.headers['Cookie'] = creds.eschol.cookie

    def send(self, query):
        data = {'query': query}
        
        try:
            response = requests.post(self.endpoint, json.dumps(data).encode('utf-8'), self.headers)
            return response.text
        except Exception as e:
            print(e)
            raise e

########################################
#
# Uses escholClient to connect with eschol
# Provides functionality for id minting and deposit 
#
########################################
class eschol:
    """Interface to connect to eschol"""

    mintMutation = '''
                mutation{
                    mintProvisionalID(input:{sourceName: "etd_proc", sourceID: "PUB_ID" })
                    {
                    id
                    }
                }
                '''


    depositMutation = '''
            mutation{
              depositItem(input:{DEP_INPUT})
              {
                id
                message
              }
            }
            '''

    def __init__(self):
        self.client = graphClient(creds.eschol.url)

    def createItem(self, pubId):
        mintquery = self.mintMutation.replace("PUB_ID",str(pubId))
        result = self.client.send(mintquery)
        print(result)
        res = json.loads(result)
        return res['data']['mintProvisionalID']['id']


    def depositItem(self, depositInput):
        depositquery = self.depositMutation.replace("DEP_INPUT",depositInput)
        result = self.client.send(depositquery)
        return result
