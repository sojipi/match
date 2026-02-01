"""
WebSocket connection manager for real-time features.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from datetime import datetime

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time features."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Connect a user to a session."""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        self.active_connections[session_id].append(websocket)
        self.user_sessions[user_id] = session_id
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Disconnect a user from a session."""
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def broadcast_to_session(self, message: dict, session_id: str):
        """Broadcast a message to all connections in a session."""
        if session_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections[session_id].remove(connection)


manager = ConnectionManager()


@router.websocket("/session/{session_id}")
async def websocket_session_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for AI matching sessions."""
    # In a real implementation, you would extract user_id from authentication
    user_id = "placeholder-user-id"
    
    await manager.connect(websocket, session_id, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "user_feedback":
                # Handle user feedback during AI conversation
                response = {
                    "type": "feedback_received",
                    "message": "Feedback received and sent to AI agents",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await manager.send_personal_message(response, websocket)
            
            elif message_data.get("type") == "request_compatibility_update":
                # Send mock compatibility update
                compatibility_update = {
                    "type": "compatibility_update",
                    "overall_score": 0.78,
                    "dimension_scores": {
                        "personality": 0.82,
                        "communication": 0.75,
                        "values": 0.80,
                        "lifestyle": 0.74
                    },
                    "trending_direction": "improving",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await manager.broadcast_to_session(compatibility_update, session_id)
            
            # Simulate AI conversation messages (for demo purposes)
            if message_data.get("type") == "start_conversation":
                await simulate_ai_conversation(session_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id, user_id)
        
        # Notify other users in the session
        await manager.broadcast_to_session({
            "type": "user_disconnected",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }, session_id)


async def simulate_ai_conversation(session_id: str):
    """Simulate AI conversation for demo purposes."""
    # This is a placeholder - in real implementation, this would trigger actual AI agents
    
    messages = [
        {
            "type": "ai_message",
            "sender_type": "user_avatar",
            "sender_name": "Alex's Avatar",
            "content": "Hi there! I'm really excited to get to know you better.",
            "emotion_indicators": ["excited", "friendly"],
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "type": "ai_message",
            "sender_type": "user_avatar", 
            "sender_name": "Sarah's Avatar",
            "content": "Hello! I'm looking forward to our conversation too. What do you like to do for fun?",
            "emotion_indicators": ["curious", "warm"],
            "timestamp": datetime.utcnow().isoformat()
        }
    ]
    
    # Send messages with delays to simulate real conversation
    for message in messages:
        await asyncio.sleep(2)  # 2 second delay between messages
        await manager.broadcast_to_session(message, session_id)