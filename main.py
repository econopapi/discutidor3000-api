import logging
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from structures import ChatRequest, ChatResponse
from discutidor3000 import Discutidor3000

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Discutidor3000 with API key from environment
discutidor = Discutidor3000(api_key=os.getenv("DEEPSEEK_API_KEY"))

api = FastAPI()

@api.get("/")
def hola():
    return {"mensaje": "Hola Mundo!"}

@api.post("/api/v1/chat")
def chat_endpoint(request: ChatRequest):
    try:
        response = discutidor.chat(
            message=request.message,
            conversation_id=request.conversation_id)
        
        if response is None:
            return {
                "error": "Error en la conversación, inténtalo de nuevo.",
                "response": None
            }
        
        return JSONResponse(
            status_code=200,
            content=response.model_dump())
    
    except Exception as e:
        logger.error(f"Error en el endpoint /api/v1/chat: {e}")
        return {
            "error": str(e),
            "response": None
        }
