
from fastapi import FastAPI
from routers import api
# , authentication

app = FastAPI()

app.include_router(api.router)
# app.include_router(authentication.router)

@app.get('/')
def index():
    return {'data': {'name':'Welcome to Contract Analyser application'}}


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=9000, log_level="info")
