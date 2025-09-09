
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.endpoints import chat_router

api = FastAPI()

api.include_router(chat_router,
                   prefix="/api/v1",
                   tags=["chat"])

@api.get("/")
def hola():
    return JSONResponse(
        status_code=200,
        content={"message": "Discutidor3000 API - Endpoint disponible: POST /api/v1/chat"})   
