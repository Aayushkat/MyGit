#filename= Health_test.py
from fastapi import APIRouter


router=APIRouter()

@router.get("/health")
def health():
    return {"status":"ok"}