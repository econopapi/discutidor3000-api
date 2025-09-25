"""
Tests para RedisService
Cubre todas las operaciones de Redis con mocks
"""

import unittest
from unittest.mock import patch, Mock
import json
import redis
import pytest

from api.services.redis import RedisService
from api.structures import Conversation, Message

class TestRedisService(unittest.TestCase):

    def setUp(self):
        """Setup para cada test."""
        with patch('api.services.redis.redis.Redis.from_url'):
            self.redis_service = RedisService()

    def test_init_success(self):
        """Test de inicialización exitosa."""
        with patch('api.services.redis.redis.Redis.from_url') as mock_redis:
            service = RedisService()
            mock_redis.assert_called_once()

    def test_set_conversation_success(self):
        """Test de almacenar conversación exitosamente."""
        conversation = Conversation(
            conversation_id="test_id",
            posture="Test posture",
            messages=[Message(role="user", content="Test message")],
            created_at="2025-03-25T12:00:00",
            last_updated="2025-03-25T12:00:00"
        )
        
        with patch.object(self.redis_service.redis, 'setex') as mock_setex:
            mock_setex.return_value = True
            
            result = self.redis_service.set_conversation("test_id", conversation)
            self.assertTrue(result)
            mock_setex.assert_called_once()

    def test_set_conversation_redis_error(self):
        """Test de error de Redis al almacenar conversación."""
        conversation = Conversation(
            conversation_id="test_id",
            posture="Test posture",
            messages=[],
            created_at="2025-03-25T12:00:00",
            last_updated="2025-03-25T12:00:00"
        )
        
        with patch.object(self.redis_service.redis, 'setex') as mock_setex:
            mock_setex.side_effect = redis.RedisError("Connection error")
            
            result = self.redis_service.set_conversation("test_id", conversation)
            self.assertFalse(result)

    def test_get_conversation_success(self):
        """Test de obtener conversación exitosamente."""
        conversation_data = {
            "conversation_id": "test_id",
            "posture": "Test posture",
            "messages": [{"role": "user", "content": "Test message"}],
            "created_at": "2025-03-25T12:00:00",
            "last_updated": "2025-03-25T12:00:00"
        }
        
        with patch.object(self.redis_service.redis, 'get') as mock_get:
            mock_get.return_value = json.dumps(conversation_data)
            
            result = self.redis_service.get_conversation("test_id")
            self.assertIsInstance(result, Conversation)
            self.assertEqual(result.conversation_id, "test_id")

    def test_get_conversation_not_found(self):
        """Test de conversación no encontrada."""
        with patch.object(self.redis_service.redis, 'get') as mock_get:
            mock_get.return_value = None
            
            result = self.redis_service.get_conversation("test_id")
            self.assertIsNone(result)

    def test_get_conversation_redis_error(self):
        """Test de error de Redis al obtener conversación."""
        with patch.object(self.redis_service.redis, 'get') as mock_get:
            mock_get.side_effect = redis.RedisError("Connection error")
            
            result = self.redis_service.get_conversation("test_id")
            self.assertIsNone(result)

    def test_get_conversation_json_decode_error(self):
        """Test de error de decodificación JSON."""
        with patch.object(self.redis_service.redis, 'get') as mock_get:
            mock_get.return_value = "invalid json"
            
            result = self.redis_service.get_conversation("test_id")
            self.assertIsNone(result)

    def test_get_all_conversations_success(self):
        """Test de obtener todas las conversaciones exitosamente."""
        with patch.object(self.redis_service.redis, 'keys') as mock_keys:
            mock_keys.return_value = ["conversation:1", "conversation:2"]
            
            result = self.redis_service.get_all_conversations()
            self.assertEqual(len(result), 2)

    def test_get_all_conversations_empty(self):
        """Test de obtener conversaciones cuando no hay ninguna."""
        with patch.object(self.redis_service.redis, 'keys') as mock_keys:
            mock_keys.return_value = []
            
            result = self.redis_service.get_all_conversations()
            self.assertIsNone(result)

    def test_get_all_conversations_redis_error(self):
        """Test de error de Redis al obtener todas las conversaciones."""
        with patch.object(self.redis_service.redis, 'keys') as mock_keys:
            mock_keys.side_effect = redis.RedisError("Connection error")
            
            result = self.redis_service.get_all_conversations()
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()