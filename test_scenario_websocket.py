"""
Test script to verify scenario simulation WebSocket broadcasting.
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from app.websocket.manager import manager

async def test_broadcast():
    """Test if broadcast_to_session works correctly."""
    
    # Simulate a session_id
    test_session_id = "e6e1cd0f-880e-41b2-b314-e03c69a9bf29"
    
    print(f"Testing broadcast to session: {test_session_id}")
    print(f"Active sessions: {list(manager.session_connections.keys())}")
    print(f"Session connections count: {len(manager.session_connections)}")
    
    # Try to broadcast a test message
    test_message = {
        "type": "test",
        "content": "This is a test message",
        "timestamp": "2026-02-09T18:00:00"
    }
    
    await manager.broadcast_to_session(test_message, test_session_id)
    print("Broadcast completed")

if __name__ == "__main__":
    asyncio.run(test_broadcast())
