from pydantic import BaseModel as Base
from typing import List, Optional

"""Estructuras de datos para el proyecto."""

class Message(Base):
    """Estructura para mensajes en la conversación."""
    role: str  # "user" o "assistant"
    content: str


class ChatRequest(Base):
    """Estructura para request de chat."""
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(Base):
    """Estructura para response de chat."""
    conversation_id: str
    message: List[Message] # 5 mensajes más recientes
