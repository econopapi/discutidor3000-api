"""
Tests para los endpoints de la API
Cubre todos los endpoints y casos de error
"""

import unittest
import os
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from api.endpoints.endpoints import chat_router
from api.services.discutidor3000 import ConversationNotFoundError, PostureExtractionError
from api.structures import ChatResponse, Message

# Crear una aplicación FastAPI para testing
app = FastAPI()
app.include_router(chat_router, prefix="/api/v1")
client = TestClient(app)

class TestEndpoints(unittest.TestCase):

    def test_hola_endpoint(self):
        """Test del endpoint raíz."""
        response = client.get("/api/v1/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Discutidor3000 API", response.json()["mensaje"])

    @patch('api.endpoints.endpoints.discutidor')
    def test_chat_endpoint_success(self, mock_discutidor):
        """Test del endpoint de chat exitoso."""
        mock_response = ChatResponse(
            conversation_id="test_id",
            message=[Message(role="user", content="Test message")]
        )
        mock_discutidor.chat.return_value = mock_response
        
        response = client.post(
            "/api/v1/chat",
            json={"message": "Test message", "conversation_id": None}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("conversation_id", response.json())

    @patch('api.endpoints.endpoints.discutidor')
    def test_chat_endpoint_none_response(self, mock_discutidor):
        """Test del endpoint de chat con respuesta None."""
        mock_discutidor.chat.return_value = None
        
        response = client.post(
            "/api/v1/chat",
            json={"message": "Test message", "conversation_id": None}
        )
        
        self.assertEqual(response.status_code, 500)

    @patch('api.endpoints.endpoints.discutidor')
    def test_chat_endpoint_conversation_not_found(self, mock_discutidor):
        """Test del endpoint de chat con conversación no encontrada."""
        mock_discutidor.chat.side_effect = ConversationNotFoundError("Conversation not found")
        
        response = client.post(
            "/api/v1/chat",
            json={"message": "Test message", "conversation_id": "nonexistent"}
        )
        
        self.assertEqual(response.status_code, 404)

    @patch('api.endpoints.endpoints.discutidor')
    def test_chat_endpoint_posture_extraction_error(self, mock_discutidor):
        """Test del endpoint de chat con error de extracción de postura."""
        mock_discutidor.chat.side_effect = PostureExtractionError("Cannot extract posture")
        
        response = client.post(
            "/api/v1/chat",
            json={"message": "Test message", "conversation_id": None}
        )
        
        self.assertEqual(response.status_code, 500)

    @patch('api.endpoints.endpoints.discutidor')
    def test_chat_endpoint_generic_error(self, mock_discutidor):
        """Test del endpoint de chat con error genérico."""
        mock_discutidor.chat.side_effect = Exception("Generic error")
        
        response = client.post(
            "/api/v1/chat",
            json={"message": "Test message", "conversation_id": None}
        )
        
        self.assertEqual(response.status_code, 500)

    @patch('api.endpoints.endpoints.discutidor')
    def test_conversations_endpoint_success(self, mock_discutidor):
        """Test del endpoint de conversaciones exitoso."""
        mock_discutidor.get_all_conversations.return_value = {
            "conversations": ["conversation:1", "conversation:2"]
        }
        
        response = client.get("/api/v1/conversations")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("conversations", response.json())

    @patch('api.endpoints.endpoints.discutidor')
    def test_conversations_endpoint_none_result(self, mock_discutidor):
        """Test del endpoint de conversaciones con resultado None."""
        mock_discutidor.get_all_conversations.return_value = None
        
        response = client.get("/api/v1/conversations")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["conversations"], {})

    @patch('api.endpoints.endpoints.discutidor')
    def test_conversations_endpoint_error(self, mock_discutidor):
        """Test del endpoint de conversaciones con error."""
        mock_discutidor.get_all_conversations.side_effect = Exception("Database error")
        
        response = client.get("/api/v1/conversations")
        
        self.assertEqual(response.status_code, 500)

    def test_chat_endpoint_invalid_request(self):
        """Test del endpoint de chat con request inválido."""
        response = client.post("/api/v1/chat", json={"invalid": "data"})
        
        self.assertEqual(response.status_code, 422)  # Validation error

if __name__ == '__main__':
    unittest.main()