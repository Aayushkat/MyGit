import httpx
from fastapi import HTTPException #for This is for client errors, invalid authentication, invalid data, etc. 
                                    #Not for server errors in your code.
from App.config import settings# directly immported the settings object fromt the config.py file


