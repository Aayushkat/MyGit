#filename=username.py
from fastapi import APIRouter

router=APIRouter()

@router.get("/users/{username}")
def get_users(username:str)->dict:
    return {"Username":username,"Followers":0}