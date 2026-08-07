from fastapi import FastAPI

app=FastAPI(title="Mygit")

@app.get("/hello")
async def root():
    return {"Message": " Hello World"}

