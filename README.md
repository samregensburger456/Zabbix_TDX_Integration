TDX Zabbix SSL Automated Ticket Creation Project
By: Samuel Regensburger

The purpose of this project is to automatically create TDX Tickets when an SSL Cert is about to expire.

Setup:
1. rename the .envSAMPLE file to .env
2. define the values in the .env file accordingly (e.g. ZABBIX_URL=zabbixserv2000.test.com)
3. run src/install_pip_dependencies.bat to install python dependencies necessary for the project to run