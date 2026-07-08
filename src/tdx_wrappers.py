#library for making HTTP requests
import requests

#A class used for interfacing with the Web API of team dynamix using python
#this class will have methods that can do things like creating tickets and searching up information on accounts
class TDX_Instance:
    #upon instantiation, take the URL to TDX, the API user's username and password, and retrieve the API token for use in later methods
    def __init__(self,tdxURL,tdxUsername,tdxPassword):
        self.URL = tdxURL
        self.USERNAME = tdxUsername
        self.PASSWORD = tdxPassword

        #define datatype as json for payload
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        #payload that has the username and password for TDX in JSON format
        payload = {
            "username": self.USERNAME,
            "password": self.PASSWORD
        }
        #URL for API page
        self.API_URL = self.URL+"/TDWebApi/api"

        #post username and password to TDX API authorization page to recieve TDX API token 
        response = requests.post(self.API_URL+"/auth",json=payload,headers=headers)

        self.API_KEY = response.text
        #the HTTP authentication header that should be used when required to authenticate a request with the API Token
        self.AUTHENTICATION_HEADER = {
            "Authorization": "Bearer "+self.API_KEY,
        }
    #method used for getting information on a specific account by name
    def getAccountID(self,accountName):
        payload = {
            "SearchText": accountName
        }
        response = requests.post(self.API_URL+"/accounts/search",json=payload,headers=self.AUTHENTICATION_HEADER)
        return response.json()
    #method for retrieving a list of all ticket types in TDX
    def getTicketTypeID(self):
        response = requests.get(self.API_URL+"/2437/tickets/types",headers=self.AUTHENTICATION_HEADER)
        return response.json()
    #method used for getting information on a specific group in TDX by name
    def getGroup(self,groupName):
         payload = {
              "NameLike": groupName
         }
         response = requests.post(self.API_URL+"/groups/search",json=payload,headers=self.AUTHENTICATION_HEADER)
         return response.json()
    #method used for creating tickets. only takes the necessary information for the request to function
    def createTicket(self,title,description,typeID,accountID,responsibleGroupID):
        #payload to be sent to TDX for the creation of the ticket
        payload = {
            "Title": title,
            "Description": description,
            "TypeID": typeID,
            "AccountID": accountID,
            "ResponsibleGroupID": responsibleGroupID,
        }
        #post request to create ticket with our custom json payload
        response = requests.post(self.API_URL+"/2437/tickets",json=payload,headers=self.AUTHENTICATION_HEADER)
        return response


