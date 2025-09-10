"""
Tests para la lógica principal de Discutidor3000
(api.services.discutidor3000.Discutidor3000)

Estos tests usan unittest y mock para simular dependencias externas.
10 tests que cubren:
- Inicialización del objeto Discutidor3000 (test_init_success, test_init_no_api_key)
- Generación del system prompt (test_gen_system_prompt)
- Solicitud a la API de DeepSeek (test_api_request)
- Obtención de la postura del mensaje inicial (test_get_posture)
- Inicialización de la conversación (test_init_conversation)
- Generación de la respuesta del bot (test_gen_response)
- Formateo de la respuesta (test_format_response)
- Iniciar nueva conversación (test_chat_new_conversation)
- Continuar conversación existente (test_continue_conversation)
"""

import unittest
from unittest.mock import patch, Mock
from api.services.discutidor3000 import Discutidor3000
from api.structures import ChatResponse, Message, Conversation

class TestDiscutidor3000(unittest.TestCase):

    def setUp(self):
        """Configuración de fixtures para cada test."""
        self.api_key = "test_api_key"
        self.discutidor = Discutidor3000(api_key=self.api_key)

    
    def test_init_success(self):
        """Test de inicialización de objeto exitosa.
        Verifica que los atributos mínimos se configuren correctamente."""
        self.assertEqual(self.discutidor.api_key, self.api_key)
        self.assertEqual(self.discutidor.api_base, "https://api.deepseek.com")
        self.assertEqual(self.discutidor.api_endpoint, "/chat/completions")
        self.assertEqual(self.discutidor.model, "deepseek-chat")
        self.assertIsNotNone(self.discutidor.redis)


    def test_init_no_api_key(self):
        """Test de inicialización de objeto sin API Key.
        Verifica que se lance ValueError si no se proporciona api_key."""
        with self.assertRaises(ValueError) as context:
            Discutidor3000(api_key=None)


    def test_gen_system_prompt(self):
        """Test de generación del system prompt.
        Verifica que el prompt generado contenga la postura dada."""
        posture = "Python debería ser un lenguaje de programación tipado estáticamente."
        prompt = self.discutidor._gen_system_prompt(posture)
        self.assertIn(posture, prompt)
        self.assertIn(
            f"Recuerda, tu objetivo es defender la postura: {posture}",
            prompt)
        

    @patch('api.services.discutidor3000.requests.post')
    def test_api_request(self, mock_post):
        """Test de solicitud a API de DeepSeek.
        Verifica que la solicitud se realice correctamente y se maneje la respuesta."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test_id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "deepseek-chat",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Test response"
                    },
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 10,
                "total_tokens": 20,
                "prompt_tokens_details": {
                    "cached_tokens": 0
                },
                "prompt_cache_hit_tokens": 0,
                "prompt_cache_miss_tokens": 10
            },
            "system_fingerprint": "test_fingerprint"}
        mock_post.return_value = mock_response
        messages = [{"role": "user", "content": "Test"}]
        result = self.discutidor._api_request(messages)
        self.assertIsNotNone(result)
        self.assertEqual(result["choices"][0]["message"]["content"], "Test response")


    @patch.object(Discutidor3000, '_api_request')
    def test_get_posture(self, mock_api_request):
        """Test de obtención de postura del mensaje inicial"""
        mock_api_request.return_value = {
            "choices": [{"message": {"content": { "posture": "Test posture" }}}]
        }

        message = "Defiende que Python debería ser un lenguaje de programación tipado estáticamente."
        result = self.discutidor._get_posture(message)
        self.assertEqual(result, "Test posture")


    @patch('api.services.discutidor3000.datetime')
    def test_init_conversation(self, mock_datetime):
        """Test de inicialización de conversación.
        Verifica que la conversación se inicie y registre correctamente."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-03-25T12:00:00"
        with patch.object(self.discutidor.redis, 'set_conversation') as mock_set:
            mock_set.return_value = True
            conversation_id = "test_id"
            posture = "Test posture"
            initial_message = "Test message"
            self.discutidor._init_conversation(
                conversation_id, posture, initial_message)
            mock_set.assert_called_once()


    @patch('api.services.discutidor3000.datetime')
    def test_gen_response(self, mock_datetime):
        """Test de generación de respuesta."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-03-25T12:00:00"
        conversation = Conversation(
            conversation_id="test_id",
            posture="Test posture",
            messages=[
                Message(role="system", content="System prompt"),
                Message(role="user", content="User message")
            ],
            created_at=mock_datetime.now.return_value.isoformat(),
            last_updated=mock_datetime.now.return_value.isoformat())
        

    def test_format_response(self):
        """Test de formateo de respuesta."""
        conversation_data = {
            "conversation_id": "test_id",
            "messages": [
                {"role": "system", "content": "System prompt"},
                {"role": "user", "content": "User message"},
                {"role": "assistant", "content": "Assistant message"} ]}
        result = self.discutidor._format_response(conversation_data)
        self.assertIsInstance(result, ChatResponse)
        self.assertEqual(result.conversation_id, "test_id")
        self.assertEqual(len(result.message), 2)


    @patch.object(Discutidor3000, 'new_conversation')
    def test_chat_new_conversation(self, mock_new_conversation):
        """Test de método para iniciar nueva conversación."""
        mock_response = {"conversation_id": "test_id", "response": "Bot response"}
        mock_new_conversation.return_value = mock_response
        
        with patch.object(self.discutidor, '_format_response') as mock_format:
            mock_format.return_value = ChatResponse(conversation_id="test_id", message=[])
            
            result = self.discutidor.chat("Test message")
            
            mock_new_conversation.assert_called_once_with("Test message")
            mock_format.assert_called_once_with(mock_response)    


    @patch.object(Discutidor3000, 'continue_conversation')
    def test_continue_conversation(self, mock_continue):
        """Test de método para continuar conversación existente."""
        mock_response = {
            "conversation_id": "test_id",
            "response": "Bot response" }
        mock_continue.return_value = mock_response
        with patch.object(self.discutidor, '_format_response') as mock_format:
            mock_format.return_value = ChatResponse(
                conversation_id="test_id",
                message = [])
            result = self.discutidor.chat(
                message="Test message",
                conversation_id="test_id")


    


