import os, json, redis, logging
from typing import Optional

logger = logging.getLogger(__name__)

from ..structures.structures import Conversation

class RedisService:
    """Servicio para interactuar con Redis."""
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis = redis.Redis.from_url(
            self.redis_url,
            decode_responses=True,
            socket_timeout=5,
            retry_on_timeout=True)
        

    def set_conversation(self, conversation_id: str,
                         conversation_data: Conversation,
                         ttl:int = 1_120_000) -> bool:
        """Almacena conversación en Redis por 2 semanas (por defecto)
        Args:
            conversation_id (str): ID de la conversación
            conversation_data (Conversation): Datos de la conversación
        Returns:
            bool: True si se almacenó correctamente, False si hubo error"""
        try:
            return self.redis.setex(
                f"conversation:{conversation_id}",
                ttl,
                json.dumps(conversation_data.model_dump()))
        except redis.RedisError as e:
            logger.error(f"Error al guardar conversación en Redis: {e}")
            logger.debug(f"Datos: {conversation_data}")
            logger.debug(f"e.args: {e.args}\nexc_info: {e.__traceback__}")
            return False
        
    
    def get_conversation(self, conversation_id: str) -> bool:
        """Obtiene conversación de Redis
        Args:
            conversation_id (str): ID de la conversación
        Returns:
            bool: True si se obtuvo correctamente, False si hubo error"""
        try:
            data = self.redis.get(f"conversation:{conversation_id}")
            if data:
                return Conversation.model_validate(json.loads(data))
            return None
        except redis.RedisError as e:
            logger.error(f"Error al obtener conversación de Redis: {e}")
            logger.debug(f"conversation_id: {conversation_id}")
            logger.debug(e.with_traceback(e.__traceback__))
            logger.debug(f"Data obtenida: {data}")
            return None
        

    def get_all_conversations(self) -> Optional[dict]:
        """Obtiene todas las conversaciones almacenadas en Redis
        Returns:
            Optional[dict]: Diccionario con todas las conversaciones o None si hubo error"""
        try:
            keys = self.redis.keys("conversation:*")
            if not keys:
                logger.debug("No se encontraron conversaciones en Redis.")
                return None
            return keys
        except redis.RedisError as e:
            logger.error(f"Error al obtener todas las conversaciones de Redis: {e}")
            logger.debug(e.with_traceback(e.__traceback__))
            return None
    
