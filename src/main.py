#import logging and rotating file handlers
import logging
from logging.handlers import RotatingFileHandler

#create a new logger and set its logging level to errors
logger = logging.getLogger("main_error_logger")
logger.setLevel(logging.ERROR)

#create a new rotating file handler so the logs don't fill up indefinitely and set the max file size to 1 megabyte
handler = RotatingFileHandler(
    "logs/errors.log",
    maxBytes = 1024 * 1024,
    backupCount=0
)
#set the formatter so that log files are displayed in an ordered and easily legible way
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
)
#apply the formatter
handler.setFormatter(formatter)
#add the log handler
logger.addHandler(handler)

#import sys so we can exit program with non error status code later
import sys
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
#import file logging

#The main function for this program
def main():
    #load the .env file and specify that it is one directory higher in the project tree than the folder this file is located
    load_dotenv(Path(__file__).parent.parent / ".env")

    #retrieve the necessary Zabbix information from the .env file and define them in constants
    ZABBIX_URL = os.getenv("ZABBIX_URL")
    ZABBIX_API_TOKEN = os.getenv("ZABBIX_API_TOKEN")
    ZABBIX_WEBSITES_HOST_GROUP_NAME = os.getenv("ZABBIX_WEBSITES_HOST_GROUP_NAME")

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
    #the name of the ticket status that indicates an SSL cert ticket is still active
    TDX_ACTIVE_STATUS_NAME=os.getenv("TDX_ACTIVE_STATUS_NAME")
    #the TDX app ID
    TDX_APP_ID=os.getenv("TDX_APP_ID")
    #the minimum number of days an SSL cert can get to before it will trigger a ticket alert | also needs to be cast to int because the .getenv will create it as a string by default
    SSL_MIN_DAYS_BEFORE_ALERT=int(os.getenv("SSL_MIN_DAYS_BEFORE_ALERT"))

    #Exception to throw if connection to Zabbix Server fails
    try:
        #Create the Zabbix API Object
        #AT THIS TIME, ZABBIX DOES NOT HAVE AN SSL CERT ISSUED BY A CA, THEREFORE VALIDATE CERTS IS SET TO FALSE. SET TO TRUE BEFORE PUTTING THIS SCRIPT INTO PRODUCTION
        zabbixAPI = ZabbixAPI(url=ZABBIX_API_URL, validate_certs = False)
    except Exception:
        raise Exception("Error connecting to Zabbix Server. Please ensure correct ZABBIX_URL in .env and check SSL cert validity")
        
    #Authenticate with Zabbix using API Token
    zabbixAPI.login(token=ZABBIX_API_TOKEN)

    #create a new TDX instance object for easy ticket creation
    TDX_INSTANCE = tdx_wrappers.TDX_Instance(TDX_URL,TDX_USERNAME,TDX_PASSWORD,TDX_APP_ID)

    #ID of ticket Type in TDX that should be assigned to the created ticket
    TICKET_TYPE_ID = -1
    #ID of the account in TDX that should be assigned to the created ticket
    ACCOUNT_ID = -1
    #ID of the account in TDX that should be assigned to the created ticket
    RESPONSIBLE_GROUP_ID = -1
    #ID of the active status in the users TDX environment to be used to check whether an SSL cert ticket is active or not
    ACTIVE_STATUS_ID = -1

    #retrieve all ticket types from TDX and save the ID where ticketType name is the same as TDX_TICKET_TYPE_NAME, since this will be the type we will assign the Zabbix ticket we create to
    ticketTypes = TDX_INSTANCE.getTicketTypes()
    for ticketType in ticketTypes:
        if ticketType['Name'] == TDX_TICKET_TYPE_NAME:
            TICKET_TYPE_ID = ticketType['ID']

    if TICKET_TYPE_ID == -1:
        raise tdx_wrappers.TDX_Error("ticket type name "+TDX_TICKET_TYPE_NAME+" does not exist | please reconfigure in .env")

    #get the Account ID via account name of the account the ticket will be created under
    accounts = TDX_INSTANCE.getAccountID(TDX_ACCOUNT_NAME)

    #catch index out of range error and print that this means TDX_TICKET_TYPE_NAME is not a real TICKET TYPE NAME in TDX
    try:
        ACCOUNT_ID = accounts[0]["ID"]
    except IndexError:
        raise tdx_wrappers.TDX_Error("account name "+TDX_ACCOUNT_NAME+" does not exist | please reconfigure in .env")

    #get the group ID of the TDX_RESPONSIBLE_GROUP_NAME
    group = TDX_INSTANCE.getGroup(TDX_RESPONSIBLE_GROUP_NAME)
    #catch index out of range error and print that this means value of TDX_RESPONSIBLE_GROUP_NAME does not exist in TDX
    try:
        RESPONSIBLE_GROUP_ID = group[0]["ID"]
    except IndexError:
        raise tdx_wrappers.TDX_Error("group name "+TDX_RESPONSIBLE_GROUP_NAME+" does not exist | please reconfigure in .env")

    #------------------------------------------------------------------------------------------------------------------------
    #This block of code will retrieve all statuses from TDX, and search for the ID of the status that is to be used as the Active Status
    #if an SSL ticket has the active status, this script will not create another SSL cert alert for that ticket, but instead just update the number of days left before the cert expires to be accurate
    #------------------------------------------------------------------------------------------------------------------------
    #get json list of all statuses from TDX
    statuses = TDX_INSTANCE.getStatuses()  
    #iterate through statuses until the active status defined in the .env is found 
    #when it is found, assign its value to the ACTIVE_STATUS_ID
    for status in statuses:
        if status["Name"] == TDX_ACTIVE_STATUS_NAME:
            ACTIVE_STATUS_ID = status["ID"]
    #if the status name does not exist in TDX, throw an error
    if(ACTIVE_STATUS_ID == -1):
        raise tdx_wrappers.TDX_Error("Status name "+TDX_ACTIVE_STATUS_NAME+" does not exist | please reconfigure in .env")

    #an array of all active SSL tickets, meant to be used later to keep inventory over what websites already have SSL alert tickets active    
    activeSSLTickets = TDX_INSTANCE.getActiveTicketsByTypeID(TICKET_TYPE_ID,ACTIVE_STATUS_ID,100)
    ###########################################################################
    ###########################################################################
    ###########################################################################

    #ZABBIX: create an object for the 'Websites' Zabbix group
    websitesGroup = zabbixAPI.hostgroup.get(
        filter={"name": ZABBIX_WEBSITES_HOST_GROUP_NAME},
        output=["groupid", "name"]
    )

    #try catch for if websites group defined in .env does not exist in zabbix
    try:
        #ZABBIX: get the group id of the zabbixwebsites group
        groupID = websitesGroup[0]["groupid"]
    except IndexError:
        raise Exception("defined Websites Group does not exist in zabbix. Please check WEBSITES_HOST_GROUP_NAME in .env")


    #get all hosts from the 'Websites' group and put them into an array
    hosts = zabbixAPI.host.get(
        groupids=groupID,
        output=["hostid", "host", "name"]
    )
    #this block of code will iterate through all of the hosts in the group that contains info on website certs in zabbix
    #if a cert in any of the websites in this host group will expire in less than 14 days, it will put in a ticket in TDX
    #this ticket will contain the name of the website, and in how many days the SSL cert will expire at the time of ticket creation
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

            #check if the days left on this host is less than the minimum days before alert
            if daysLeft < SSL_MIN_DAYS_BEFORE_ALERT:
                #variable to denote whether the ticket exists or not so we know whether to make a new one or if we can just modify an existing one
                ticketExists = False
                #Description string to be used as the description for the ticket
                description = host["host"]+" SSL Certificate expiring in "+str(daysLeft)+" days. New Update"
                #iterate through the active SSL tickets. if a ticket for the current host already exists, simply modify the the description to update the number of days left until it expires
                for ticket in activeSSLTickets:
                    if host['host'] in ticket['Title']:
                        TDX_INSTANCE.changeTicketDescription(ticket['ID'],description)
                        ticketExists = True
                        break
                #if the ticket for this hosts SSL cert doesn't exist, create one
                if(not ticketExists):
                    TDX_INSTANCE.createTicket("SSL Cert expiring for "+host['host'],description,TICKET_TYPE_ID,ACCOUNT_ID,RESPONSIBLE_GROUP_ID)

#variable to store the path to the email flag
emailFlag = Path("logs/hasEmailed")
#Run the main function in a try catch so we can log any exceptions that occur within in our rotating file log
try:
    main()
    #if the program erred the last time it ran and an email was send, but this time it ran successfully, delete the email flag so the next time it errs, the email flag can be raised again
    if emailFlag.exists():
        emailFlag.unlink()
except Exception as exception:
    #log the error
    logger.exception(exception)
    #if the script erred the last time it ran, this means an email was already sent. we want to exit with a non error code now, since the script this will be ran with will only email if the program exits with a non zero code
    #if it doesn't exists, this means its the first instance of it erring, therefore create the email flag and exit the program with an exception, e.g. non zero status code
    if emailFlag.exists():
        sys.exit(0)
    else:
        emailFlag.touch()
    #we raise an exception here in the program itsself even though we already logged it so that we can indicate to the process that executed the file that it ended with an error
    raise exception