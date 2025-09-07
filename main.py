from fastapi import FastAPI

api = FastAPI()

@api.get("/")
def hola():
    return {"mensaje": "Hola Mundo!"}
    