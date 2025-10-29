# this script is workaround in case Merritt callback arrived but was not added to DB
# grep jid error_log.2025.10.24 | grep job:jobState

import re
import json
import creds
import mysql.connector
import argparse



class processLog:
    logEntries = []
    insertInfo = "insert into merrittcallbacks (jid, callbackdata) VALUES ('{param1}','{param2}') "
    getInfo = "select id from merrittcallbacks where jid = '{param1}'"
    def __init__(self, logentries):
        self.cnxn = mysql.connector.connect(user=creds.etdDb.username, 
                        password=creds.etdDb.password,
                        host=creds.etdDb.server,
                        database=creds.etdDb.database,
                        charset='utf8mb4',
                        port=creds.etdDb.port, 
                        auth_plugin='mysql_native_password')
        self.cursor = self.cnxn.cursor()
        self.logEntries = logentries

    def isJidPresent(self, jid):
        query = self.getInfo.format(param1=jid)
        self.cursor.execute(query)
        result = None
        for row in self.cursor:
            result = row[0]
        return result != None

    def savePayload(self, jid, payload):
        query = self.insertInfo.format(param1=jid, param2=payload)
        self.cursor.execute(query)
        self.cnxn.commit()

    def processAll(self):
        for payload in self.logEntries:
            jid = payload['job:jobState']['job:jobID']
            if self.isJidPresent(jid) == False:
                self.savePayload(jid, json.dumps(payload,ensure_ascii=False))
            else:
                print(f'skipped {jid}')

# Set up argument parser
parser = argparse.ArgumentParser(description='Extract JSON payloads from a log file.')
parser.add_argument('input_file', help='Path to the input log file')
args = parser.parse_args()

# Regular expression to match JSON payloads inside curly braces
json_pattern = re.compile(r'(\{.*\})')

# List to store extracted JSON objects
extracted_json = []
with open(args.input_file, 'r') as file:
    for line in file:
        match = json_pattern.search(line)
        if match:
            try:
                # Parse the matched string as JSON
                payload = json.loads(match.group(1))
                print(payload)
                print(payload['job:jobState']['job:jobID'])
                extracted_json.append(payload)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON: {match.group(1)}")

x = processLog(extracted_json)
x.processAll()