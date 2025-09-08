import logging
from fastapi import FastAPI
from structures import ChatRequest
from chat_service import chat

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

api = FastAPI()

@api.get("/")
def hola():
    return {"mensaje": "Hola Mundo!"}


@api.post("/api/v1/chat")
def chat_endpoint(request: ChatRequest):
    try:
        response = chat(
            message=request.message,
            conversation_id=request.conversation_id)
        
        if response is None:
            return {
                "error": "Error en la conversación, inténtalo de nuevo.",
                "response": None
            }
        
        return {
            "conversation_id": response["conversation_id"],
            "response": response
        }
    except Exception as e:
        logger.error(f"Error en el endpoint /api/v1/chat: {e}")
        return {
            "error": str(e),
            "response": None
        }
