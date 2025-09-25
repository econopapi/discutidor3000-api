"""
Tests de integración que prueban el flujo completo
"""

import unittest
from unittest.mock import patch, Mock
import json

from api.services.discutidor3000 import Discutidor3000
from api.structures import Conversation, Message

class TestIntegration(unittest.TestCase):

    def setUp(self):
        """Setup para tests de integración."""
        with patch('api.services.discutidor3000.RedisService'):
            self.discutidor = Discutidor3000(api_key="test_api_key")

    @patch('api.services.discutidor3000.requests.post')
    def test_complete_new_conversation_flow(self, mock_post):
        """Test del flujo completo de nueva conversación."""
        # Mock para extracción de postura
        posture_response = Mock()
        posture_response.status_code = 200
        posture_response.json.return_value = {
            "choices": [{"message": {"content": '{"posture": "Python is better than Java"}'}}]
        }
        
        # Mock para respuesta del bot
        chat_response = Mock()
        chat_response.status_code = 200
        chat_response.json.return_value = {
            "choices": [{"message": {"content": "I totally agree! Python is superior because..."}}]
        }
        
        mock_post.side_effect = [posture_response, chat_response]
        
        with patch.object(self.discutidor.redis, 'set_conversation') as mock_set:
            with patch.object(self.discutidor.redis, 'get_conversation') as mock_get:
                mock_set.return_value = True
                mock_get.return_value = Conversation(
                    conversation_id="test_id",
                    posture="Python es mejor que JavaScript",
                    messages=[
                        Message(role="system", content="System prompt"),
                        Message(role="user", content="Defiende que Python es mejor que JavaScript"),
                        Message(role="assistant", content="Totalmente de acuerdo! Python es superior porque...")
                    ],
                    created_at="2025-03-25T12:00:00",
                    last_updated="2025-03-25T12:00:00"
                )
                
                with patch('api.services.discutidor3000.uuid4') as mock_uuid:
                    mock_uuid.return_value = Mock()
                    mock_uuid.return_value.__str__ = Mock(return_value="test_id")
                    
                    result = self.discutidor.chat("Defend that Python is better than Java")
                    
                    self.assertIsNotNone(result)
                    self.assertEqual(result.conversation_id, "test_id")

    def test_complete_continue_conversation_flow(self):
        """Test del flujo completo de continuar conversación."""
        existing_conversation = Conversation(
            conversation_id="test_id",
            posture="Python is better than Java",
            messages=[
                Message(role="system", content="System prompt"),
                Message(role="user", content="Previous message")
            ],
            created_at="2025-03-25T11:00:00",
            last_updated="2025-03-25T11:00:00"
        )
        
        with patch.object(self.discutidor.redis, 'get_conversation') as mock_get:
            with patch.object(self.discutidor.redis, 'set_conversation') as mock_set:
                with patch('api.services.discutidor3000.requests.post') as mock_post:
                    mock_get.return_value = existing_conversation
                    mock_set.return_value = True
                    
                    chat_response = Mock()
                    chat_response.status_code = 200
                    chat_response.json.return_value = {
                        "choices": [{"message": {"content": "Continuing the argument..."}}]
                    }
                    mock_post.return_value = chat_response
                    
                    result = self.discutidor.chat("Tell me more", "test_id")
                    
                    self.assertIsNotNone(result)
                    self.assertEqual(result.conversation_id, "test_id")

    def test_error_handling_chain(self):
        """Test de manejo de errores en cadena."""
        with patch.object(self.discutidor, '_get_posture') as mock_posture:
            mock_posture.return_value = None
            
            with self.assertRaises(Exception):
                self.discutidor.chat("Test message")

if __name__ == '__main__':
    unittest.main()