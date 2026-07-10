TDX Zabbix SSL Automated Ticket Creation Project
By: Samuel Regensburger

The purpose of this project is to automatically create TDX Tickets when an SSL Cert is about to expire.

Setup:
1. rename the .envSAMPLE file to .env
2. define the values in the .env file accordingly (e.g. ZABBIX_URL=zabbixserv2000.test.com)
3. run src/install_pip_dependencies.bat to install python dependencies necessary for the project to run

Below is an explanation of every .env value that you need to configure.

ZABBIX_URL=The Base URL of your Zabbix Server
ZABBIX_API_TOKEN=The Full API token for the User in Zabbix you wish to use
ZABBIX_WEBSITES_HOST_GROUP_NAME=
TDX_URL=The Base URL of your TDX Instance
TDX_USERNAME=The Username of the user who you want to access the Team Dynamix API
TDX_PASSWORD=The password for this Team Dynamix user
TDX_TICKET_TYPE_NAME=The name of the Team Dynamix Ticket Type you want the SSL Tickets to fall under
TDX_ACCOUNT_NAME=The name of the Team Dynamixaccount/dept who you want the SSL Tickets to fall under
TDX_RESPONSIBLE_GROUP_NAME=The name of the Team Dynamix group you want to be responsible for the SSL Tickets
TDX_ACTIVE_STATUS_NAME=The name of the status in your TDX environment that would be considered an Active Ticket
TDX_APP_ID=The APP ID of the Team Dynamix App you want to use for this script
SSL_MIN_DAYS_BEFORE_ALERT=The minimum number of days before an SSL cert is going to expire that will cause a ticket to be submitted