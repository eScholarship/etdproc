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
        self.cookies = None
        self.headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'Privileged':creds.eschol.privKey
                   }
        if creds.eschol.cookie:
            self.cookies = dict(ACCESS_COOKIE=creds.eschol.cookie)

    def send(self, query, param):
        data = {'query': query, "variables": param}
        
        try:
            response = requests.post(self.endpoint, json = data, headers = self.headers, cookies = self.cookies)
            # Print response
            print(f"Response: {response.status_code} -- {response.reason}")
            print(response)
            return response.status_code, response.text
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
    deposit = "mutation depositItem($input: DepositItemInput!){ depositItem(input: $input) { message } }"
    mint = "mutation mintProvisionalID($input: MintProvisionalIDInput!){ mintProvisionalID(input: $input) { id } }"

    def __init__(self):
        self.client = graphClient(creds.eschol.url)

    def createItem(self, pubId):
        # to do create etd_proc
        mintparam = {"input": {'sourceName': "etd_proc", 'sourceID': pubId }}
        #mintquery = self.mintMutation.replace("PUB_ID",str(pubId))
        code, result = self.client.send(self.mint, mintparam)
        print(result)
        if code == 200:
            res = json.loads(result)
            return code, res['data']['mintProvisionalID']['id']
        return code, result


    def depositItem(self, depositInput):
        #depositquery = self.depositMutation.replace("DEP_INPUT",depositInput)
        depositparam = {"input": depositInput}
        code, result = self.client.send(self.deposit, depositparam)
        return code, result
