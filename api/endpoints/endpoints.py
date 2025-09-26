from ..structures import ChatRequest
from ..services.discutidor3000 import (
    Discutidor3000,
    ConversationNotFoundError,
    PostureExtractionError
)

import os, logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
discutidor = Discutidor3000(api_key=os.getenv("OPENROUTER_API_KEY"))
chat_router = APIRouter()

@chat_router.get("/")
def hola():
    return JSONResponse(
        status_code=200,
        content={"mensaje": "Discutidor3000 API - Endpoint disponible: POST /chat"})


@chat_router.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        response = discutidor.chat(
            message=request.message,
            conversation_id=request.conversation_id)
        if response is None:
            raise HTTPException(status_code=500,
                                 detail="Error en la conversación, inténtalo de nuevo.")
        return JSONResponse(
            status_code=200,
            content=response.model_dump())
    
    except ConversationNotFoundError as cnfe:
        logger.error(f"Conversación no encontrada en el endpoint /chat: {cnfe}")
        raise HTTPException(status_code=404, detail=str(cnfe))
    except PostureExtractionError as pee:
        logger.error(f"Error de extracción de postura en el endpoint /chat: {pee}")
        raise HTTPException(status_code=500, detail=str(pee))
    except Exception as e:
        logger.error(f"Error en el endpoint /chat: {e}")
        logger.debug(f"Trazo completo del error:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

@chat_router.get("/conversations")
def get_conversations():
    try:
        conversations = discutidor.get_all_conversations()
        return JSONResponse(
            status_code=200,
            content={"conversations": conversations or {}})
    except Exception as e:
        logger.error(f"Error en el endpoint /conversations: {e}")
        logger.debug(f"Trazo completo del error:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))