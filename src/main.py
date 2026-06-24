#add functionality to read from .env file in specific format
from dotenv import load_dotenv
#import pathlib for specifying path to .env
from pathlib import Path
#import zabbix API
from zabbix_utils import ZabbixAPI
#import OS for reading raw data from .env
import os

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
zabbix_API = ZabbixAPI(url=ZABBIX_API_URL, validate_certs = False)

#Login to zabbix using the API token
zabbix_API.login(token=ZABBIX_API_TOKEN)

#query the zabbix api object to make a request for the API version
print("Connected! API Version:", zabbix_API.api_version())


