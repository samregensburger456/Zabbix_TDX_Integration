#set the context that the script runs in to the directory this script is located in
Set-Location -Path $PSScriptRoot
#install all pip dependencies
pip install dotenv pathlib zabbix_utils datetime requests
#Create the logs directory
mkdir "$PSScriptRoot\logs\"
