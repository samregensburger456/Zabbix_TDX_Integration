#library for making HTTP requests
import requests

#A class used for interfacing with the Web API of team dynamix using python
#this class will have methods that can do things like creating tickets
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
    
        #store the API key returned by the post request as an attribute
        self.API_KEY = response.text

