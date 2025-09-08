from pydantic import BaseModel as Base
from typing import Optional

"""Estructuras de datos para el proyecto."""

class ChatRequest(Base):
    message: str
    conversation_id: Optional[str] = None

