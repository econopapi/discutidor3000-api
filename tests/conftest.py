import sys
import os
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Agregar el directorio raíz al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture
def mock_redis():
    """Fixture para mockear Redis."""
    with patch('api.services.redis.redis.Redis.from_url') as mock:
        redis_instance = Mock()
        mock.return_value = redis_instance
        yield redis_instance

@pytest.fixture
def mock_discutidor_redis():
    """Fixture específico para mockear Redis en Discutidor3000."""
    with patch('api.services.discutidor3000.RedisService') as mock:
        redis_service = Mock()
        mock.return_value = redis_service
        yield redis_service

@pytest.fixture
def sample_conversation():
    """Fixture con una conversación de ejemplo."""
    from api.structures import Conversation, Message
    return Conversation(
        conversation_id="test_id",
        posture="Test posture",
        messages=[
            Message(role="system", content="System prompt"),
            Message(role="user", content="User message")
        ],
        created_at="2025-03-25T12:00:00",
        last_updated="2025-03-25T12:00:00"
    )

@pytest.fixture
def sample_message():
    """Fixture con un mensaje de ejemplo."""
    from api.structures import Message
    return Message(role="user", content="Test message")

@pytest.fixture
def api_key():
    """Fixture con API key de prueba."""
    return "test_api_key"

@pytest.fixture
def mock_datetime():
    """Fixture para mockear datetime."""
    with patch('api.services.discutidor3000.datetime') as mock_dt:
        mock_dt.now.return_value.isoformat.return_value = "2025-03-25T12:00:00"
        yield mock_dt