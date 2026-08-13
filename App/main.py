#filename=main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from App.routers import hello                #importing hello.py, from path App/routers which denoted by "from App.routers" 
from App.routers import Health_test          #importing Healht_test.py from path App/routers 
from App.routers import username


app=FastAPI(title="Mygit")
#The 'router=APIrouter()' inside the the file hello.py
app.include_router(hello.router) 
app.include_router(Health_test.router)
app.include_router(username.router)





#fastapi only returns JSON thats why we have a response class
## To return HTML instead, we can use FastAPI's HTMLResponse class.View
#https://fastapi.tiangolo.com/advanced/custom-response/

@app.get("/",response_class=HTMLResponse)#to handle the get request sent by browser/curl/client accesing our server
def home():
    return "<h1>This will become the GITHUB Portfolio</h1>"

