import logging
import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.endpoints import chat_router

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Configurar root_path basado en variable de entorno
root_path = os.getenv("ROOT_PATH", "")

api = FastAPI(
    title="Discutidor3000 API",
    description="API para chatbot argumentativo",
    version="1.0.0",
    root_path=root_path
)

api.include_router(chat_router,
                   prefix="/api/v1",
                   tags=["chat"])

@api.get("/")
def hola():
    return JSONResponse(
        status_code=200,
        content={"message": "Discutidor3000 API - Endpoint disponible: POST /api/v1/chat"})