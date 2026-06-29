#add functionality to read from .env file in specific format
from dotenv import load_dotenv
#import pathlib for specifying path to .env
from pathlib import Path
#import zabbix API
from zabbix_utils import ZabbixAPI
#import OS for reading raw data from .env
import os
#import datetime for converting times recieved from zabbix to a human readable format
from datetime import datetime
#import ticket creation module
import TDX_Wrappers

#load the .env file and specify that it is one directory higher in the project tree than the folder this file is located
load_dotenv(Path(__file__).parent.parent / ".env")

#retrieve the Zabbix URL from the .env file and define it
ZABBIX_URL = os.getenv("ZABBIX_URL")

#retrieve Zabbix API token from .env and define it
ZABBIX_API_TOKEN = os.getenv("ZABBIX_API_TOKEN")

#define the URL for the zabbix API file
ZABBIX_API_URL = ZABBIX_URL + "/api_jsonrpc.php"

#Create the Zabbix API Object
#AT THIS TIME, ZABBIX DOES NOT HAVE AN SSL CERT ISSUED BY A CA, THEREFORE VALIDATE CERTS IS SET TO FALSE. SET TO TRUE BEFORE PUTTING THIS SCRIPT INTO PRODUCTION
zabbixAPI = ZabbixAPI(url=ZABBIX_API_URL, validate_certs = False)

#Login to zabbix using the API token
zabbixAPI.login(token=ZABBIX_API_TOKEN)

#query the zabbix api object to make a request for the API version
print("Connected! API Version:", zabbixAPI.api_version())

#create an object for the 'Websites' Zabbix group
websitesGroup = zabbixAPI.hostgroup.get(
    filter={"name": "Websites"},
    output=["groupid", "name"]
)

#get the group id of the websites group
groupID = websitesGroup[0]["groupid"]

#get all hosts from the 'Websites' group and put them into an array
hosts = zabbixAPI.host.get(
    groupids=groupID,
    output=["hostid", "host", "name"]
)

#iterate through hosts array
for host in hosts:
    #put all items from current host into items array
    items = zabbixAPI.item.get(
        hostids=host["hostid"],
        search={"name": "Expires on"},
    )
    #iterate through items
    for item in items:
        #if the host has Expires on attribute blank, skip the host
        if not item["lastvalue"]:
            continue
        #expiration date of SSL cert in Unix time format
        expiry = datetime.fromtimestamp(int(item["lastvalue"]))
        #get the days left before the certificate expires using datetime conversions
        daysLeft = (expiry - datetime.now()).days
        #call the ticket creation function from the createTicket module.
        if daysLeft < 14:
            print(host["host"])




