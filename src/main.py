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
import tdx_wrappers

#load the .env file and specify that it is one directory higher in the project tree than the folder this file is located
load_dotenv(Path(__file__).parent.parent / ".env")

#retrieve the necessary Zabbix information from the .env file and define them in constants
ZABBIX_URL = os.getenv("ZABBIX_URL")
ZABBIX_API_TOKEN = os.getenv("ZABBIX_API_TOKEN")
WEBSITES_HOST_GROUP_NAME = os.getenv("WEBSITES_HOST_GROUP_NAME")

#define a constant specifically for accessing the API from the base URL. Should probably remove the Base URL when this is complete if it is not used and only this is used
ZABBIX_API_URL = ZABBIX_URL + "/api_jsonrpc.php"

#retrieve the necessary TDX information from the .env file and define them in constants
TDX_URL=os.getenv("TDX_URL")
TDX_USERNAME=os.getenv("TDX_USERNAME")
TDX_PASSWORD=os.getenv("TDX_PASSWORD")

#The name of the ticket type that the SSL cert tickets will be defined under
TDX_TICKET_TYPE_NAME=os.getenv("TDX_TICKET_TYPE_NAME")
#the name of the account the SSL cert ticket will be defined under
TDX_ACCOUNT_NAME=os.getenv("TDX_ACCOUNT_NAME")
#the name of the Responsible group the SSL cert ticket will be defined under
TDX_RESPONSIBLE_GROUP_NAME=os.getenv("TDX_RESPONSIBLE_GROUP_NAME")

#Create the Zabbix API Object
#AT THIS TIME, ZABBIX DOES NOT HAVE AN SSL CERT ISSUED BY A CA, THEREFORE VALIDATE CERTS IS SET TO FALSE. SET TO TRUE BEFORE PUTTING THIS SCRIPT INTO PRODUCTION
zabbixAPI = ZabbixAPI(url=ZABBIX_API_URL, validate_certs = False)

#Login to zabbix using the API token
zabbixAPI.login(token=ZABBIX_API_TOKEN)

#query the zabbix api object to make a request for the API version
print("Connected! API Version:", zabbixAPI.api_version())

#create a new TDX instance object for easy ticket creation
TDX_INSTANCE = tdx_wrappers.TDX_Instance(TDX_URL,TDX_USERNAME,TDX_PASSWORD)

#ID of ticket Type in TDX that should be assigned to the created ticket
TICKET_TYPE_ID = -1
#ID of the account in TDX that should be assigned to the created ticket
ACCOUNT_ID = -1
#ID of the account in TDX that should be assigned to the created ticket
RESPONSIBLE_GROUP_ID = -1

#retrieve all ticket types from TDX and save the ID where ticketType name is the same as TDX_TICKET_TYPE_NAME, since this will be the type we will assign the Zabbix ticket we create to
ticketTypes = TDX_INSTANCE.getTicketTypeID()
for ticketType in ticketTypes:
    if ticketType['Name'] == TDX_TICKET_TYPE_NAME:
        TICKET_TYPE_ID = ticketType['ID']

#get the Account ID via account name of the account the ticket will be created under
accounts = TDX_INSTANCE.getAccountID(TDX_ACCOUNT_NAME)
ACCOUNT_ID = accounts[0]["ID"]

#get the group ID of the TDX_RESPONSIBLE_GROUP_NAME
group = TDX_INSTANCE.getGroup(TDX_RESPONSIBLE_GROUP_NAME)
RESPONSIBLE_GROUP_ID = group[0]["ID"]
###########################################################################
###########################################################################
###########################################################################

#ZABBIX: create an object for the 'Websites' Zabbix group
websitesGroup = zabbixAPI.hostgroup.get(
    filter={"name": WEBSITES_HOST_GROUP_NAME},
    output=["groupid", "name"]
)

#ZABBIX: get the group id of the zabbixwebsites group
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