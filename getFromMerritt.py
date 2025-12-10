import requests
import urllib.parse
from creds import merritt_creds
import sys
import time
from datetime import datetime
import pytz


# ============================================================
# This is a utility to download from Merritt if needed. 
# The ETD files are removed from disk 30 days after complete processing.
# If there is a need to reprocess xml, we can download from Merritt and reprocess.
# ============================================================
def waitForMerritt(anticipated_time_str):
    if not anticipated_time_str:
        print(" No anticipated-availability-time found in response.")
        return

    # Convert to datetime object
    anticipated_time = datetime.fromisoformat(anticipated_time_str)
    now = datetime.now(anticipated_time.tzinfo)

    # Step 3: Calculate sleep duration
    wait_seconds = (anticipated_time - now).total_seconds() + 10

    if wait_seconds > 0:
        print(f"Waiting {int(wait_seconds)} seconds until {anticipated_time.isoformat()}...")
        time.sleep(wait_seconds)

    return

def getToken(ark):
    encoded_ark = urllib.parse.quote(ark, safe='')
    # Construct the full URL
    url = f"https://merritt.cdlib.org/api/assemble-obj/{encoded_ark}"

    # Send GET request with Basic Auth
    response = requests.get(url, auth=(merritt_creds.username, merritt_creds.password))


    # Check the response
    if response.status_code != 200:
        print(f"Failed with status code {response.status_code}")
        print(response.text)
        return None

    print("Success!")
    print(response.json())
    waitForMerritt(response.json()["anticipated-availability-time"])
    return response.json()['token'] 

def downloadZip(token):
    url = "https://merritt.cdlib.org/api/presign-obj-by-token/" + token
    # Send GET request with redirect handling
    response = requests.get(url, allow_redirects=True)

    # Polling loop
    while True:
        response = requests.get(url, allow_redirects=True)
    
        if response.status_code == 200:
            with open("merritt.zip", "wb") as f:
                f.write(response.content)
            print("File downloaded successfully as merritt.zip")
            break
        elif response.status_code == 202:
            print("File not ready yet. Waiting 60 seconds before retrying...")
            time.sleep(60)
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(response.text)
            break


# Make sure args are provided
if len(sys.argv) < 2:
  sys.stderr.write("Usage: %s ark\n" % sys.argv[0])
  sys.stderr.write("... where ark is full Merritt ark such as ark:/13030/m5jr2stz \n")
  sys.exit(1)

merrittArk = sys.argv[1]

token = getToken(merrittArk)
if token:
    downloadZip(token)
