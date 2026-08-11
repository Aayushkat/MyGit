#filename=hello.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router=APIRouter()
@router.get("/hello",response_class=HTMLResponse)
def hello():
    return "<h1> HELLO </h1>"