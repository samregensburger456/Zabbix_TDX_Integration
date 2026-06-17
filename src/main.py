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

#define the ZABBIX_URL
ZABBIX_URL = os.getenv("ZABBIX_URL")

#defube the Zabbix API token
ZABBIX_API_TOKEN = os.getenv("ZABBIX_API_TOKEN")

#define the URL for the zabbix API file
ZABBIX_API_URL = ZABBIX_URL + "/api_jsonrpc.php"

#define where any requests to the zabbix API will go. 
#Since SSL certs are not setup at the time of writing this script, we will skip validation
zabbix_API = ZabbixAPI(url=ZABBIX_API_URL, validate_certs = False)

#use the zabbix api object we just created to make a login request
zabbix_API.login(token=ZABBIX_API_TOKEN)

#query the zabbix api object to make a request for the API version
print("Connected! API Version:", zabbix_API.api_version())

