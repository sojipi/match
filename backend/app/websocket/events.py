"""
WebSocket event handlers and real-time event management.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from app.websocket.manager import manager
from app.models.conversation import ConversationSession, ConversationMessage, SessionStatus
from app.models.match import Match, MatchStatus

logger = logging.getLogger(__name__)


class WebSocketEventHandler:
    """
    Handles real-time events and coordinates WebSocket communications.
    Manages AI conversation events, compatibility updates, and user interactions.
    """
    
    def __init__(self):
        self.active_ai_sessions: Dict[str, Dict] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.processing_events = False
    
    async def start_event_processing(self):
        """Start the event processing loop."""
        if self.processing_events:
            return
        
        self.processing_events = True
        asyncio.create_task(self._process_events())
        logger.info("WebSocket event processing started")
    
    async def stop_event_processing(self):
        """Stop the event processing loop."""
        self.processing_events = False
        logger.info("WebSocket event processing stopped")
    
    async def _process_events(self):
        """Process events from the queue."""
        while self.processing_events:
            try:
                # Wait for events with timeout
                event = await asyncio.wait_for(
                    self.event_queue.get(), 
                    timeout=1.0
                )
                await self._handle_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
    
    async def _handle_event(self, event: Dict[str, Any]):
        """Handle a specific event."""
        event_type = event.get("type")
        
        if event_type == "ai_message":
            await self._handle_ai_message(event)
        elif event_type == "compatibility_update":
            await self._handle_compatibility_update(event)
        elif event_type == "session_status_change":
            await self._handle_session_status_change(event)
        elif event_type == "user_action":
            await self._handle_user_action(event)
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    async def _handle_ai_message(self, event: Dict[str, Any]):
        """Handle AI-generated messages."""
        session_id = event.get("session_id")
        message_data = event.get("message_data", {})
        
        # Add message metadata
        message_data.update({
            "type": "ai_message",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Broadcast to session viewers
        await manager.broadcast_to_session(message_data, session_id)
        
        # Update session activity
        if session_id in self.active_ai_sessions:
            self.active_ai_sessions[session_id]["last_message"] = datetime.utcnow()
            self.active_ai_sessions[session_id]["message_count"] += 1
    
    async def _handle_compatibility_update(self, event: Dict[str, Any]):
        """Handle compatibility score updates."""
        session_id = event.get("session_id")
        compatibility_data = event.get("compatibility_data", {})
        
        # Format compatibility update
        update_message = {
            "type": "compatibility_update",
            "session_id": session_id,
            **compatibility_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to session viewers
        await manager.broadcast_to_session(update_message, session_id)
    
    async def _handle_session_status_change(self, event: Dict[str, Any]):
        """Handle session status changes."""
        session_id = event.get("session_id")
        new_status = event.get("status")
        
        status_message = {
            "type": "session_status_change",
            "session_id": session_id,
            "status": new_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to session viewers
        await manager.broadcast_to_session(status_message, session_id)
        
        # Update active sessions tracking
        if new_status == "completed" and session_id in self.active_ai_sessions:
            del self.active_ai_sessions[session_id]
    
    async def _handle_user_action(self, event: Dict[str, Any]):
        """Handle user actions during sessions."""
        session_id = event.get("session_id")
        user_id = event.get("user_id")
        action_data = event.get("action_data", {})
        
        action_message = {
            "type": "user_action",
            "session_id": session_id,
            "user_id": user_id,
            **action_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to session viewers
        await manager.broadcast_to_session(action_message, session_id)
    
    # Public methods for triggering events
    
    async def trigger_ai_message(
        self, 
        session_id: str, 
        sender_type: str,
        sender_name: str,
        content: str,
        emotion_indicators: List[str] = None,
        compatibility_impact: float = None
    ):
        """Trigger an AI message event."""
        event = {
            "type": "ai_message",
            "session_id": session_id,
            "message_data": {
                "message_id": f"msg_{datetime.utcnow().timestamp()}",
                "sender_type": sender_type,
                "sender_name": sender_name,
                "content": content,
                "emotion_indicators": emotion_indicators or [],
                "compatibility_impact": compatibility_impact
            }
        }
        
        await self.event_queue.put(event)
    
    async def trigger_compatibility_update(
        self,
        session_id: str,
        overall_score: float,
        dimension_scores: Dict[str, float],
        trending_direction: str = "stable",
        key_insights: List[str] = None,
        conversation_highlights: List[Dict] = None
    ):
        """Trigger a compatibility update event."""
        event = {
            "type": "compatibility_update",
            "session_id": session_id,
            "compatibility_data": {
                "overall_score": overall_score,
                "dimension_scores": dimension_scores,
                "trending_direction": trending_direction,
                "key_insights": key_insights or [],
                "conversation_highlights": conversation_highlights or []
            }
        }
        
        await self.event_queue.put(event)
    
    async def trigger_session_status_change(self, session_id: str, status: str):
        """Trigger a session status change event."""
        event = {
            "type": "session_status_change",
            "session_id": session_id,
            "status": status
        }
        
        await self.event_queue.put(event)
    
    async def trigger_user_action(
        self,
        session_id: str,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any] = None
    ):
        """Trigger a user action event."""
        event = {
            "type": "user_action",
            "session_id": session_id,
            "user_id": user_id,
            "action_data": {
                "action_type": action_type,
                **(action_data or {})
            }
        }
        
        await self.event_queue.put(event)
    
    async def start_ai_session(
        self,
        session_id: str,
        user1_id: str,
        user2_id: str,
        session_type: str = "conversation"
    ):
        """Start an AI matching session."""
        # Initialize session tracking
        self.active_ai_sessions[session_id] = {
            "user1_id": user1_id,
            "user2_id": user2_id,
            "session_type": session_type,
            "started_at": datetime.utcnow(),
            "last_message": datetime.utcnow(),
            "message_count": 0,
            "status": "active"
        }
        
        # Trigger session start event
        await self.trigger_session_status_change(session_id, "active")
        
        # Start AI conversation simulation (in real implementation, this would trigger actual AI agents)
        asyncio.create_task(self._simulate_ai_conversation(session_id))
    
    async def _simulate_ai_conversation(self, session_id: str):
        """Simulate an AI conversation for demo purposes."""
        if session_id not in self.active_ai_sessions:
            return
        
        session_data = self.active_ai_sessions[session_id]
        
        # Simulate conversation flow
        conversation_flow = [
            {
                "sender_type": "user_avatar",
                "sender_name": "Alex's Avatar",
                "content": "Hi! I'm excited to meet you. I noticed we both love hiking - what's your favorite trail?",
                "emotion_indicators": ["excited", "curious"],
                "compatibility_impact": 0.05,
                "delay": 2
            },
            {
                "sender_type": "user_avatar",
                "sender_name": "Sarah's Avatar",
                "content": "Hello! That's so cool that you hike too! I absolutely love the Pacific Crest Trail. Have you been there?",
                "emotion_indicators": ["enthusiastic", "connected"],
                "compatibility_impact": 0.08,
                "delay": 3
            },
            {
                "sender_type": "user_avatar",
                "sender_name": "Alex's Avatar",
                "content": "No way! I've been planning a PCT section hike for months. What section did you do?",
                "emotion_indicators": ["amazed", "excited"],
                "compatibility_impact": 0.12,
                "delay": 2
            },
            {
                "sender_type": "user_avatar",
                "sender_name": "Sarah's Avatar",
                "content": "I did the Oregon section last summer - it was incredible! The views around Crater Lake were breathtaking. We should definitely talk more about hiking!",
                "emotion_indicators": ["passionate", "inviting"],
                "compatibility_impact": 0.15,
                "delay": 4
            }
        ]
        
        current_compatibility = 0.65
        
        for i, message in enumerate(conversation_flow):
            if session_id not in self.active_ai_sessions:
                break
            
            # Wait for delay
            await asyncio.sleep(message["delay"])
            
            # Send AI message
            await self.trigger_ai_message(
                session_id=session_id,
                sender_type=message["sender_type"],
                sender_name=message["sender_name"],
                content=message["content"],
                emotion_indicators=message["emotion_indicators"],
                compatibility_impact=message["compatibility_impact"]
            )
            
            # Update compatibility after significant messages
            if message["compatibility_impact"] > 0.1:
                current_compatibility += message["compatibility_impact"]
                await asyncio.sleep(1)  # Brief pause before compatibility update
                
                await self.trigger_compatibility_update(
                    session_id=session_id,
                    overall_score=min(current_compatibility, 1.0),
                    dimension_scores={
                        "personality": min(0.70 + (i * 0.05), 1.0),
                        "communication": min(0.68 + (i * 0.04), 1.0),
                        "values": min(0.72 + (i * 0.06), 1.0),
                        "lifestyle": min(0.75 + (i * 0.03), 1.0)
                    },
                    trending_direction="improving",
                    key_insights=[
                        "Strong shared interest in outdoor activities",
                        "Similar adventure-seeking personalities",
                        "Natural conversation flow"
                    ],
                    conversation_highlights=[
                        {
                            "message_id": f"msg_{datetime.utcnow().timestamp()}",
                            "highlight": "Discovered mutual passion for hiking",
                            "impact": message["compatibility_impact"]
                        }
                    ]
                )
        
        # End session after conversation
        await asyncio.sleep(5)
        await self.trigger_session_status_change(session_id, "completed")


# Global event handler instance
event_handler = WebSocketEventHandler()


# Utility functions for external services

async def start_websocket_events():
    """Start WebSocket event processing."""
    await event_handler.start_event_processing()


async def stop_websocket_events():
    """Stop WebSocket event processing."""
    await event_handler.stop_event_processing()


async def create_ai_matching_session(
    session_id: str,
    user1_id: str,
    user2_id: str,
    session_type: str = "conversation"
):
    """Create and start an AI matching session."""
    await event_handler.start_ai_session(session_id, user1_id, user2_id, session_type)


async def send_ai_message_to_session(
    session_id: str,
    sender_type: str,
    sender_name: str,
    content: str,
    emotion_indicators: List[str] = None,
    compatibility_impact: float = None
):
    """Send an AI message to a session."""
    await event_handler.trigger_ai_message(
        session_id, sender_type, sender_name, content, emotion_indicators, compatibility_impact
    )


async def update_session_compatibility(
    session_id: str,
    overall_score: float,
    dimension_scores: Dict[str, float],
    trending_direction: str = "stable",
    key_insights: List[str] = None
):
    """Update session compatibility scores."""
    await event_handler.trigger_compatibility_update(
        session_id, overall_score, dimension_scores, trending_direction, key_insights
    )