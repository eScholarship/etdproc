import requests
import json
import traceback
import consts


# ============================================================
# Class Name: graphClient
# Description:
#     Interface to connect with escholAPI
#
# Attributes:
#     ep (string): URL of the end point.
#
# Usage:
#     x = graphClient(ep)
#     x.send()
#
# Notes:
#     - Exception from post request are logged in output log. 
# ============================================================
class graphClient:
    def __init__(self, ep):
        self.endpoint = ep
        self.cookies = None
        self.headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'Privileged':consts.configs['eschol.privKey']
                   }
        if "eschol.cookie" in consts.configs:
            self.cookies = dict(ACCESS_COOKIE=consts.configs['eschol.cookie'])

    ########################################
    #
    # Sends post request and saves info in log
    # for troubleshooting purposes 
    #
    ########################################
    def send(self, query, param):
        data = {'query': query, "variables": param}
        
        try:
            response = requests.post(self.endpoint, json = data, headers = self.headers, cookies = self.cookies)
            # Print response
            print(f"Response: {response.status_code} -- {response.reason}")
            print(response)
            return response.status_code, response.text
        except Exception as e:
            callstack = traceback.format_exc()
            print(callstack)
            print(e)
            raise e


# ============================================================
# Class Name: graphClient
# Description:
#   Uses escholClient to connect with eschol
#   Provides functionality for id minting and deposit 
#
#
# Usage:
#     x = eschol()
#     x.createItem()
#     x.depositItem()
#     x.replaceMeta()
# ============================================================
class eschol:
    """Interface to connect to eschol"""
    deposit = "mutation depositItem($input: DepositItemInput!){ depositItem(input: $input) { message } }"
    replacemeta = "mutation replaceMetadata($input: ReplaceMetadataInput!){ replaceMetadata(input: $input) { message } }"
    mint = "mutation mintProvisionalID($input: MintProvisionalIDInput!){ mintProvisionalID(input: $input) { id } }"

    def __init__(self):
        self.client = graphClient(consts.configs['eschol.url'])

    ########################################
    #
    # Mints Ark for a thesis 
    #
    ########################################
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

    ########################################
    #
    # Deposits to eschol sending metadata and files 
    #
    ########################################
    def depositItem(self, depositInput):
        #depositquery = self.depositMutation.replace("DEP_INPUT",depositInput)
        depositparam = {"input": depositInput}
        code, result = self.client.send(self.deposit, depositparam)
        return code, result

    ########################################
    #
    # ReplaceMetadata sends metadata only 
    #
    ########################################
    def replaceMeta(self, replaceInput):
        replaceparam = {"input": replaceInput}
        code, result = self.client.send(self.replacemeta, replaceparam)
        return code, result