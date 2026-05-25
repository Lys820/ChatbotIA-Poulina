"""
Tests Redis memory service
"""
import pytest
import asyncio
from app.services.memory_service import RedisConversationMemory


@pytest.fixture
def memory():
    """Fixture memory service"""
    return RedisConversationMemory("redis://localhost:6379")


def test_create_session(memory):
    """Test création session"""
    session_id = memory.create_session()
    assert session_id
    assert len(session_id) > 0


def test_add_exchange(memory):
    """Test ajout Q/A"""
    session_id = memory.create_session()
    
    result = memory.add_exchange(
        session_id=session_id,
        question="Quelle souche?",
        answer="Ross 308 recommandée",
        metadata={"model": "RF"}
    )
    
    assert result is True


def test_get_context_window(memory):
    """Test récupération contexte"""
    session_id = memory.create_session()
    
    # Ajoute messages
    memory.add_exchange(session_id, "Q1?", "A1")
    memory.add_exchange(session_id, "Q2?", "A2")
    memory.add_exchange(session_id, "Q3?", "A3")
    
    context = memory.get_context_window(session_id, num_messages=2)
    
    assert "Q2" in context or "Q3" in context
    assert len(context) > 0


def test_get_full_history(memory):
    """Test historique complet"""
    session_id = memory.create_session()
    
    for i in range(5):
        memory.add_exchange(session_id, f"Q{i}?", f"A{i}")
    
    history = memory.get_full_history(session_id)
    assert len(history) == 5


def test_session_stats(memory):
    """Test stats session"""
    session_id = memory.create_session()
    memory.add_exchange(session_id, "Q1?", "A1")
    
    stats = memory.get_session_stats(session_id)
    
    assert stats["message_count"] == 1
    assert "duration_seconds" in stats


def test_clear_session(memory):
    """Test suppression session"""
    session_id = memory.create_session()
    memory.add_exchange(session_id, "Q?", "A")
    
    memory.clear_session(session_id)
    
    history = memory.get_full_history(session_id)
    assert len(history) == 0


def test_active_sessions(memory):
    """Test liste sessions"""
    s1 = memory.create_session()
    s2 = memory.create_session()
    
    active = memory.get_active_sessions()
    
    assert s1 in active
    assert s2 in active


if __name__ == "__main__":
    pytest.main([__file__, "-v"])