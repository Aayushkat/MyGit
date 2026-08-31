
#---------------------TLDR-------------------------
#THis file would be essentiall for communicating between this server and github server 
#Class declared in this file ,will initialize the http requests, for API calls from Github servers 




# This package is to  initiate http client requests
import httpx




#for This is for client errors, invalid authentication, invalid data, etc. 
#Not for server errors in your code.if the gitub server throw any undesired result we can invoke methods and objects from given below package
from fastapi import HTTPException 




from App.config import settings # directly immported the settings object fromt the config.py file



class GithubClient:
    BASE="https://api.github.com"#GitHub's API only serves over 'https://.' so make sure to sue secured http 

    def __init__(self):
        self._headers = {"Accept": "application/vnd.github.v3+json",
                         "User-Agent": "github-portfolio-app"}
                #_header ,leading underscore is meaing protected and not be accesed by 'from _module_name_ import'
        
        if settings.github_token:
            self._headers["Authorization"] = f"token {settings.github_token}"
            #defining the get_user method which will be used by the instance to take usenrame and then check for any exception error and then return the data
    
    async def get_user(self,username:str)->dict:

        #making a async instance as vairable, named: 'client'
        async with httpx.AsyncClient(headers=self._headers,timeout=15.0) as client: #Make sure to pass only keyword arguemtn in the httpx.AsyncClient because it doesnt accept positional argument
            r=await client.get(f"{self.BASE}/users/{username}")


    #checking for status code then handling the error with custom details,rather than letting it handle by the framework
    # for more info https://fastapi.tiangolo.com/tutorial/handling-errors/ 
        if r.status_code==404:
            raise HTTPException(status_code=404,detail="Username doesnt exist")
        if r.status_code==403 or r.status_code==429:
            raise HTTPException(status_code=403,detail="Github limit reached,try again later")

#we cant raise custom exceptions for every status error so rest of the exceptions are raised by 'raise_for_status()' function ,as it is. 
        r.raise_for_status()
        return r.json()