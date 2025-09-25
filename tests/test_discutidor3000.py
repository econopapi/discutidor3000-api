"""
Tests para la lógica principal de Discutidor3000
Cobertura completa de todas las funcionalidades
"""

import unittest
import json
from unittest.mock import patch, Mock
import pytest

from api.services.discutidor3000 import (
    Discutidor3000, 
    ConversationNotFoundError, 
    PostureExtractionError
)
from api.structures import ChatResponse, Message, Conversation

class TestDiscutidor3000(unittest.TestCase):

    def setUp(self):
        """Configuración de fixtures para cada test."""
        self.api_key = "test_api_key"
        with patch('api.services.discutidor3000.RedisService'):
            self.discutidor = Discutidor3000(api_key=self.api_key)

    def test_init_success(self):
        """Test de inicialización exitosa."""
        self.assertEqual(self.discutidor.api_key, self.api_key)
        self.assertEqual(self.discutidor.api_base, "https://api.deepseek.com")
        self.assertEqual(self.discutidor.model, "deepseek-chat")
        self.assertIsNotNone(self.discutidor.redis)

    def test_init_no_api_key(self):
        """Test de inicialización sin API key."""
        with self.assertRaises(ValueError) as context:
            with patch('api.services.discutidor3000.RedisService'):
                Discutidor3000(api_key=None)
        self.assertIn("API key is required", str(context.exception))

    def test_gen_system_prompt(self):
        """Test de generación del system prompt."""
        posture = "Python es mejor que Java"
        prompt = self.discutidor._gen_system_prompt(posture)
        self.assertIn(posture, prompt)
        self.assertIn("defender la postura", prompt)

    @patch('api.services.discutidor3000.requests.post')
    def test_api_request_success(self, mock_post):
        """Test de solicitud exitosa a API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response

        result = self.discutidor._api_request([{"role": "user", "content": "test"}])
        self.assertIsNotNone(result)
        self.assertEqual(result["choices"][0]["message"]["content"], "Test response")

    @patch('api.services.discutidor3000.requests.post')
    def test_api_request_error(self, mock_post):
        """Test de error en API request."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = self.discutidor._api_request([{"role": "user", "content": "test"}])
        self.assertIsNone(result)

    @patch('api.services.discutidor3000.requests.post')
    def test_api_request_with_json_format(self, mock_post):
        """Test de request con formato JSON."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"posture": "Test"}'}}]
        }
        mock_post.return_value = mock_response

        result = self.discutidor._api_request(
            [{"role": "user", "content": "test"}], 
            use_json=True
        )
        self.assertIsNotNone(result)

    @patch.object(Discutidor3000, '_api_request')
    def test_get_posture_success(self, mock_api_request):
        """Test de extracción exitosa de postura."""
        mock_api_request.return_value = {
            "choices": [{"message": {"content": '{"posture": "Test posture"}'}}]
        }

        result = self.discutidor._get_posture("Defend that Python is better")
        self.assertEqual(result, "Test posture")

    @patch.object(Discutidor3000, '_api_request')
    def test_get_posture_api_error(self, mock_api_request):
        """Test de error en extracción de postura."""
        mock_api_request.return_value = None

        result = self.discutidor._get_posture("Test message")
        self.assertIsNone(result)

    @patch.object(Discutidor3000, '_api_request')
    def test_get_posture_json_error(self, mock_api_request):
        """Test de error de JSON en extracción de postura."""
        mock_api_request.return_value = {
            "choices": [{"message": {"content": "invalid json"}}]
        }

        result = self.discutidor._get_posture("Test message")
        self.assertIsNone(result)

    @patch('api.services.discutidor3000.datetime')
    def test_init_conversation(self, mock_datetime):
        """Test de inicialización de conversación."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-03-25T12:00:00"
        
        with patch.object(self.discutidor.redis, 'set_conversation') as mock_set:
            mock_set.return_value = True
            
            self.discutidor._init_conversation("test_id", "test_posture", "test_message")
            mock_set.assert_called_once()

    @patch('api.services.discutidor3000.datetime')
    def test_gen_response_success(self, mock_datetime):
        """Test de generación exitosa de respuesta."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-03-25T12:00:00"
        
        conversation = Conversation(
            conversation_id="test_id",
            posture="Test posture",
            messages=[
                Message(role="system", content="System prompt"),
                Message(role="user", content="User message")
            ],
            created_at="2025-03-25T12:00:00",
            last_updated="2025-03-25T12:00:00"
        )
        
        with patch.object(self.discutidor.redis, 'get_conversation') as mock_get:
            with patch.object(self.discutidor.redis, 'set_conversation') as mock_set:
                with patch.object(self.discutidor, '_api_request') as mock_api:
                    mock_get.return_value = conversation
                    mock_set.return_value = True
                    mock_api.return_value = {
                        "choices": [{"message": {"content": "Bot response"}}]
                    }
                    
                    result = self.discutidor._gen_response("test_id")
                    self.assertIsNotNone(result)
                    self.assertEqual(result["response"], "Bot response")

    def test_gen_response_not_found(self):
        """Test de respuesta cuando no se encuentra conversación."""
        with patch.object(self.discutidor.redis, 'get_conversation') as mock_get:
            mock_get.return_value = None
            
            with self.assertRaises(ValueError):
                self.discutidor._gen_response("nonexistent_id")

    def test_format_response(self):
        """Test de formateo de respuesta."""
        conversation_data = {
            "conversation_id": "test_id",
            "messages": [
                {"role": "system", "content": "System prompt"},
                {"role": "user", "content": "User message"},
                {"role": "assistant", "content": "Assistant message"}
            ]
        }
        
        result = self.discutidor._format_response(conversation_data)
        self.assertIsInstance(result, ChatResponse)
        self.assertEqual(result.conversation_id, "test_id")
        self.assertEqual(len(result.message), 2)  # Excluding system prompt

    @patch.object(Discutidor3000, '_get_posture')
    @patch.object(Discutidor3000, '_init_conversation')
    @patch.object(Discutidor3000, '_gen_response')
    @patch('api.services.discutidor3000.uuid4')
    def test_new_conversation_success(self, mock_uuid, mock_gen, mock_init, mock_posture):
        """Test de nueva conversación exitosa."""
        mock_uuid.return_value = Mock()
        mock_uuid.return_value.__str__ = Mock(return_value="test_id")
        mock_posture.return_value = "Test posture"
        mock_gen.return_value = {
            "conversation_id": "test_id",
            "response": "Bot response",
            "messages": []
        }
        
        with patch.object(self.discutidor, '_format_response') as mock_format:
            mock_format.return_value = ChatResponse(conversation_id="test_id", message=[])
            
            result = self.discutidor.new_conversation("Test message")
            self.assertIsNotNone(result)

    @patch.object(Discutidor3000, '_get_posture')
    def test_new_conversation_posture_error(self, mock_posture):
        """Test de error al extraer postura en nueva conversación."""
        mock_posture.return_value = None
        
        with self.assertRaises(PostureExtractionError):
            self.discutidor.new_conversation("Test message")

    @patch.object(Discutidor3000, '_gen_response')
    @patch('api.services.discutidor3000.datetime')
    def test_continue_conversation_success(self, mock_datetime, mock_gen):
        """Test de continuar conversación existente."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-03-25T12:00:00"
        
        conversation = Conversation(
            conversation_id="test_id",
            posture="Test posture",
            messages=[Message(role="user", content="Previous message")],
            created_at="2025-03-25T11:00:00",
            last_updated="2025-03-25T11:00:00"
        )
        
        mock_gen.return_value = {
            "conversation_id": "test_id",
            "response": "Bot response",
            "messages": []
        }
        
        with patch.object(self.discutidor.redis, 'get_conversation') as mock_get:
            with patch.object(self.discutidor.redis, 'set_conversation') as mock_set:
                with patch.object(self.discutidor, '_format_response') as mock_format:
                    mock_get.return_value = conversation
                    mock_set.return_value = True
                    mock_format.return_value = ChatResponse(conversation_id="test_id", message=[])
                    
                    result = self.discutidor.continue_conversation("test_id", "New message")
                    self.assertIsNotNone(result)

    def test_continue_conversation_not_found(self):
        """Test de continuar conversación inexistente."""
        with patch.object(self.discutidor.redis, 'get_conversation') as mock_get:
            mock_get.return_value = None
            
            with self.assertRaises(ConversationNotFoundError):
                self.discutidor.continue_conversation("nonexistent_id", "Test message")

    @patch.object(Discutidor3000, 'new_conversation')
    def test_chat_new_conversation(self, mock_new):
        """Test de chat con nueva conversación."""
        mock_new.return_value = ChatResponse(conversation_id="test_id", message=[])
        
        result = self.discutidor.chat("Test message")
        mock_new.assert_called_once_with("Test message")

    @patch.object(Discutidor3000, 'continue_conversation')
    def test_chat_continue_conversation(self, mock_continue):
        """Test de chat continuando conversación."""
        mock_continue.return_value = ChatResponse(conversation_id="test_id", message=[])
        
        result = self.discutidor.chat("Test message", "test_id")
        mock_continue.assert_called_once_with("test_id", "Test message")

    def test_get_all_conversations_success(self):
        """Test de obtener todas las conversaciones exitosamente."""
        with patch.object(self.discutidor.redis, 'get_all_conversations') as mock_get:
            mock_get.return_value = ["conversation:1", "conversation:2"]
            
            result = self.discutidor.get_all_conversations()
            self.assertIsNotNone(result)
            self.assertIn("conversations", result)

    def test_get_all_conversations_error(self):
        """Test de error al obtener conversaciones."""
        with patch.object(self.discutidor.redis, 'get_all_conversations') as mock_get:
            mock_get.side_effect = Exception("Redis error")
            
            result = self.discutidor.get_all_conversations()
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()