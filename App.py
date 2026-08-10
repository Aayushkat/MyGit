from fastapi import FastAPI
from fastapi.responses import HTMLResponse#https://fastapi.tiangolo.com/advanced/custom-response/


app=FastAPI(title="Mygit")

@app.get("/hello")
def hello():
    return {"Message": " Hello World"}



#fastapi only returns JSON thats 
@app.get("/",response_class=HTMLResponse)
def home():
    return "<h1>This will become the GITHUB Portfolio</h1>"

