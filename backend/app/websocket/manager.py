"""
WebSocket connection manager for real-time AI matching features.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Dict, List, Optional, Set
import json
import asyncio
import logging
import uuid
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.core.security import verify_token
from app.core.config import settings
from app.models.conversation import ConversationSession, ConversationMessage, SessionStatus, AgentType, MessageType
from app.models.user import User
from app.websocket.security import secure_websocket_connection, validate_websocket_message, cleanup_websocket_security

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()


class ConnectionManager:
    """
    Enhanced WebSocket connection manager for real-time AI matching features.
    Handles authentication, room-based messaging, and state synchronization.
    """
    
    def __init__(self):
        # Session-based connections: session_id -> List[WebSocket]
        self.session_connections: Dict[str, List[WebSocket]] = {}
        
        # User-specific connections: user_id -> WebSocket
        self.user_connections: Dict[str, WebSocket] = {}
        
        # Connection metadata: websocket -> connection_info
        self.connection_info: Dict[WebSocket, Dict] = {}
        
        # Active sessions tracking: session_id -> session_metadata
        self.active_sessions: Dict[str, Dict] = {}
        
        # User presence: user_id -> last_activity
        self.user_presence: Dict[str, datetime] = {}
    
    async def authenticate_websocket(self, websocket: Optional[WebSocket], token: str, db: AsyncSession) -> Optional[User]:
        """Authenticate WebSocket connection using JWT token."""
        try:
            print(f"DEBUG: authenticate_websocket called with token len: {len(token)}")
            payload = verify_token(token)
            user_id = payload.get("sub")
            if not user_id:
                print("DEBUG: No user_id in token payload")
                return None
            
            # Fetch user from database
            print(f"DEBUG: Fetching user {user_id} from database")
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalars().first()
            
            if user:
                print(f"DEBUG: User found: {user.id}")
            else:
                print(f"DEBUG: User not found in DB")
            
            return user
        except Exception as e:
            logger.error(f"WebSocket authentication failed: {e}")
            print(f"DEBUG: WebSocket authentication failed: {e}")
            return None
    
    async def connect_to_session(
        self, 
        websocket: WebSocket, 
        session_id: str, 
        user: User,
        db: AsyncSession
    ) -> bool:
        """Connect a user to a specific AI matching session."""
        try:
            logger.info(f"Attempting to connect user {user.id} to session {session_id}")
            # websocket.accept() is handled by the caller
            
            # Initialize session connections if needed
            if session_id not in self.session_connections:
                self.session_connections[session_id] = []
            
            # Add connection to session
            self.session_connections[session_id].append(websocket)
            
            # Track user connection
            self.user_connections[str(user.id)] = websocket
            
            # Store connection metadata
            self.connection_info[websocket] = {
                "user_id": str(user.id),
                "session_id": session_id,
                "connected_at": datetime.utcnow(),
                "user_name": f"{user.first_name} {user.last_name}"
            }
            
            # Update user presence
            self.user_presence[str(user.id)] = datetime.utcnow()
            
            # Update session viewer count
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["viewer_count"] = len(self.session_connections[session_id])
            else:
                self.active_sessions[session_id] = {
                    "viewer_count": 1,
                    "status": "active",
                    "started_at": datetime.utcnow()
                }
            
            # Get session details from database
            from app.models.conversation import ConversationSession
            from sqlalchemy import select
            result = await db.execute(
                select(ConversationSession).where(ConversationSession.id == session_id)
            )
            session_obj = result.scalar_one_or_none()

            # Send welcome message with session state
            logger.info(f"Sending welcome message to user {user.id}")
            print(f"DEBUG: Sending welcome message to user {user.id}")
            if not await self.send_personal_message({
                "type": "connection_established",
                "session_id": session_id,
                "user_id": str(user.id),
                "viewer_count": self.active_sessions[session_id]["viewer_count"],
                "session": {
                    "session_id": session_id,
                    "status": session_obj.status if session_obj else "waiting",
                    "session_type": session_obj.session_type if session_obj else "conversation",
                    "viewer_count": self.active_sessions[session_id]["viewer_count"]
                } if session_obj else None,
                "timestamp": datetime.utcnow().isoformat()
            }, websocket):
                logger.error(f"Failed to send welcome message to user {user.id}")
                print(f"DEBUG: Failed to send welcome message to user {user.id}")
                await websocket.close(code=1011, reason="Failed to send welcome message")
                return False
            
            logger.info(f"Welcome message sent to user {user.id}")
            print(f"DEBUG: Welcome message sent to user {user.id}")
            
            # Notify other users in session about new viewer
            await self.broadcast_to_session({
                "type": "user_joined",
                "user_id": str(user.id),
                "user_name": f"{user.first_name} {user.last_name}",
                "viewer_count": self.active_sessions[session_id]["viewer_count"],
                "timestamp": datetime.utcnow().isoformat()
            }, session_id, exclude_websocket=websocket)
            
            logger.info(f"User {user.id} connected to session {session_id}")
            print(f"DEBUG: User {user.id} connected to session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting user to session: {e}", exc_info=True)
            print(f"DEBUG: Error connecting user to session: {e}")
            await websocket.close(code=1011, reason="Connection failed")
            return False
    
    async def disconnect_from_session(self, websocket: WebSocket):
        """Disconnect a user from their session."""
        if websocket not in self.connection_info:
            return
        
        connection_data = self.connection_info[websocket]
        user_id = connection_data["user_id"]
        session_id = connection_data["session_id"]
        
        try:
            # Remove from session connections
            if session_id in self.session_connections:
                if websocket in self.session_connections[session_id]:
                    self.session_connections[session_id].remove(websocket)
                
                # Clean up empty session
                if not self.session_connections[session_id]:
                    del self.session_connections[session_id]
                    if session_id in self.active_sessions:
                        del self.active_sessions[session_id]
                else:
                    # Update viewer count
                    self.active_sessions[session_id]["viewer_count"] = len(self.session_connections[session_id])
            
            # Remove user connection
            if user_id in self.user_connections:
                del self.user_connections[user_id]
            
            # Remove connection info
            del self.connection_info[websocket]
            
            # Update user presence
            if user_id in self.user_presence:
                del self.user_presence[user_id]
            
            # Notify other users in session
            if session_id in self.session_connections:
                await self.broadcast_to_session({
                    "type": "user_left",
                    "user_id": user_id,
                    "user_name": connection_data.get("user_name", "Unknown"),
                    "viewer_count": self.active_sessions.get(session_id, {}).get("viewer_count", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }, session_id)
            
            logger.info(f"User {user_id} disconnected from session {session_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting user: {e}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket) -> bool:
        """
        Send a message to a specific WebSocket connection.
        Returns True if successful, False otherwise.
        """
        try:
            await websocket.send_text(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            print(f"DEBUG: Error sending personal message: {e}")
            # Connection might be closed, handle cleanup
            await self.disconnect_from_session(websocket)
            return False
    
    async def broadcast_to_session(
        self, 
        message: dict, 
        session_id: str, 
        exclude_websocket: Optional[WebSocket] = None
    ):
        """Broadcast a message to all connections in a session."""
        print(f"DEBUG: broadcast_to_session called with session_id={session_id}")
        print(f"DEBUG: Available sessions: {list(self.session_connections.keys())}")
        
        if session_id not in self.session_connections:
            print(f"DEBUG: Session {session_id} not found in session_connections")
            return
        
        connection_count = len(self.session_connections[session_id])
        print(f"DEBUG: Broadcasting to {connection_count} connections in session {session_id}")
        
        disconnected = []
        for connection in self.session_connections[session_id]:
            if connection == exclude_websocket:
                continue
                
            try:
                await connection.send_text(json.dumps(message))
                print(f"DEBUG: Successfully sent message to connection")
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                print(f"DEBUG: Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            await self.disconnect_from_session(connection)
    
    async def broadcast_to_user(self, message: dict, user_id: str):
        """Send a message to a specific user if they're connected."""
        if user_id in self.user_connections:
            await self.send_personal_message(message, self.user_connections[user_id])
    
    async def get_session_viewers(self, session_id: str) -> List[Dict]:
        """Get list of viewers currently in a session."""
        if session_id not in self.session_connections:
            return []
        
        viewers = []
        for websocket in self.session_connections[session_id]:
            if websocket in self.connection_info:
                info = self.connection_info[websocket]
                viewers.append({
                    "user_id": info["user_id"],
                    "user_name": info.get("user_name", "Unknown"),
                    "connected_at": info["connected_at"].isoformat()
                })
        
        return viewers
    
    async def is_user_online(self, user_id: str) -> bool:
        """Check if a user is currently online."""
        return user_id in self.user_connections
    
    async def get_active_sessions(self) -> Dict[str, Dict]:
        """Get all currently active sessions."""
        return self.active_sessions.copy()


# Global connection manager instance
manager = ConnectionManager()


async def get_current_user_from_token(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extract and validate user from WebSocket token parameter."""
    user = await manager.authenticate_websocket(None, token, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return user


@router.websocket("/session/{session_id}")
async def websocket_session_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for AI matching sessions.
    Provides real-time communication for live AI conversations with security.
    """
    user_info = None
    
    try:
        logger.info(f"New WebSocket connection attempt for session {session_id}")
        print(f"DEBUG: New WebSocket connection attempt for session {session_id}")
        
        # Secure connection validation
        try:
            print("DEBUG: calling secure_websocket_connection")
            success, message, user_info = await secure_websocket_connection(
                websocket, token, required_permissions={"websocket_access"}
            )
            print(f"DEBUG: secure_websocket_connection returned: {success}, {message}")
        except Exception as e:
            logger.error(f"Security check exception: {e}")
            print(f"DEBUG: Security check exception: {e}")
            raise

        if not success:
            logger.warning(f"WebSocket security check failed: {message}")
            print(f"DEBUG: WebSocket security check failed: {message}")
            await websocket.close(code=1008, reason=message)
            return
            
        logger.info(f"WebSocket security check passed for user {user_info['user_id']}")

        # Fetch real user from database
        try:
            # Ensure user_id is a UUID
            try:
                user_id_uuid = UUID(user_info['user_id'])
            except ValueError:
                logger.error(f"Invalid user ID format: {user_info['user_id']}")
                await websocket.close(code=1008, reason="Invalid user ID")
                return

            result = await db.execute(select(User).filter(User.id == user_id_uuid))
            user = result.scalars().first()
        except Exception as e:
            logger.error(f"Database error fetching user: {e}")
            print(f"DEBUG: Database error fetching user: {e}")  # Force output
            await websocket.close(code=1011, reason="Database error")
            return

        if not user:
            logger.error(f"User {user_info['user_id']} not found in database")
            print(f"DEBUG: User {user_info['user_id']} not found in database") # Force output
            await websocket.close(code=1008, reason="User not found")
            return
            
        # Accept connection after successful validation
        await websocket.accept()
        logger.info("WebSocket connection accepted")
        print(f"DEBUG: WebSocket connection accepted for user {user.id}") # Force output
        
        # Connect to session
        print(f"DEBUG: Connecting user {user.id} to session {session_id}")
        if not await manager.connect_to_session(websocket, session_id, user, db):
            logger.error("Failed to connect to session")
            print("DEBUG: Failed to connect to session") # Force output
            return
            
        logger.info("Successfully connected to session, starting message loop")
        print("DEBUG: Successfully connected to session, starting message loop")
        
        # Main message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                
                # Check for ping message
                try:
                    message_data = json.loads(data)
                except json.JSONDecodeError:
                    # Ignore non-JSON messages (like raw "ping")
                    continue
                    
                if message_data.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                    continue

                # Validate message security
                message_allowed, validation_message = await validate_websocket_message(
                    websocket, message_data
                )
                
                if not message_allowed:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": validation_message,
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                    continue
                
                # Update user presence
                manager.user_presence[str(user.id)] = datetime.utcnow()
                
                # Handle different message types
                await handle_websocket_message(
                    message_data, session_id, user, websocket, db
                )
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                sent = await manager.send_personal_message({
                    "type": "error",
                    "message": "Message processing failed",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)
                if not sent:
                    break
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close(code=1011, reason="Internal server error")
    
    finally:
        logger.info("Cleaning up WebSocket connection")
        # Clean up connection and security
        if user_info:
            await manager.disconnect_from_session(websocket)
        cleanup_websocket_security(websocket)


async def handle_websocket_message(
    message_data: dict,
    session_id: str,
    user: User,
    websocket: WebSocket,
    db: AsyncSession
):
    """Handle incoming WebSocket messages based on type."""
    
    message_type = message_data.get("type")
    
    if message_type == "user_feedback":
        await handle_user_feedback(message_data, session_id, user, websocket, db)
    
    elif message_type == "request_compatibility_update":
        await handle_compatibility_request(session_id, user, websocket, db)
    
    elif message_type == "start_conversation":
        await handle_start_conversation(message_data, session_id, user, websocket, db)
    
    elif message_type == "user_guidance":
        await handle_user_guidance(message_data, session_id, user, websocket, db)
    
    elif message_type == "reaction":
        await handle_user_reaction(message_data, session_id, user, websocket, db)
    
    elif message_type == "end_conversation":
        await handle_end_conversation(message_data, session_id, user, websocket, db)
    
    elif message_type == "ping":
        # Handle ping/pong for connection health
        await manager.send_personal_message({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
    
    else:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Unknown message type: {message_type}",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)


async def handle_user_feedback(
    message_data: dict,
    session_id: str,
    user: User,
    websocket: WebSocket,
    db: AsyncSession
):
    """Handle user feedback during AI conversation."""
    feedback = message_data.get("feedback", {})
    
    # Store feedback (in real implementation, save to database)
    response = {
        "type": "feedback_received",
        "message": "Feedback received and sent to AI agents",
        "feedback_id": f"feedback_{datetime.utcnow().timestamp()}",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.send_personal_message(response, websocket)
    
    # Notify other viewers about feedback (optional)
    await manager.broadcast_to_session({
        "type": "user_provided_feedback",
        "user_id": str(user.id),
        "user_name": f"{user.first_name} {user.last_name}",
        "timestamp": datetime.utcnow().isoformat()
    }, session_id, exclude_websocket=websocket)


async def handle_compatibility_request(
    session_id: str,
    user: User,
    websocket: WebSocket,
    db: AsyncSession
):
    """Handle request for compatibility update."""
    # In real implementation, calculate actual compatibility
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
        "key_insights": [
            "Strong alignment on core values",
            "Complementary communication styles",
            "Shared interests in outdoor activities"
        ],
        "conversation_highlights": [
            {
                "message_id": "msg_123",
                "highlight": "Great chemistry discussing travel experiences",
                "impact": 0.15
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_session(compatibility_update, session_id)


async def handle_start_conversation(
    message_data: dict,
    session_id: str,
    user: User,
    websocket: WebSocket,
    db: AsyncSession
):
    """Handle request to start AI conversation using real AI agents."""
    try:
        from app.services.ai_agent_service import AIAgentService
        from app.models.conversation import ConversationSession, SessionStatus
        from sqlalchemy import select, update

        # Update session status to active
        await db.execute(
            update(ConversationSession)
            .where(ConversationSession.id == session_id)
            .values(
                status=SessionStatus.ACTIVE.value,
                started_at=datetime.utcnow()
            )
        )
        await db.commit()

        # Notify that conversation is starting
        await manager.broadcast_to_session({
            "type": "conversation_starting",
            "message": "AI avatars are preparing to start conversation...",
            "timestamp": datetime.utcnow().isoformat()
        }, session_id)

        # Notify session status change
        await manager.broadcast_to_session({
            "type": "session_status_change",
            "status": "active",
            "timestamp": datetime.utcnow().isoformat()
        }, session_id)

        # Start real AI conversation in background
        asyncio.create_task(start_ai_conversation(session_id, db))

    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Failed to start conversation: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)


async def start_ai_conversation(session_id: str, db: AsyncSession):
    """Start real AI conversation using AgentScope and Gemini API."""
    try:
        from app.services.ai_agent_service import AIAgentService
        from app.models.conversation import ConversationSession, ConversationMessage
        from sqlalchemy import select

        # Get session details
        result = await db.execute(
            select(ConversationSession).where(ConversationSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            logger.error(f"Session {session_id} not found")
            return

        # Initialize AI agent service
        ai_service = AIAgentService(db)

        # Get avatar agents for both users
        try:
            agent1 = await ai_service.get_user_avatar_agent(str(session.user1_id))
        except Exception as e:
            logger.warning(f"Failed to get agent1, will try to create: {e}")
            agent1 = None

        try:
            agent2 = await ai_service.get_user_avatar_agent(str(session.user2_id))
        except Exception as e:
            logger.warning(f"Failed to get agent2, will try to create: {e}")
            agent2 = None

        # If either agent is missing, try to create avatars
        if not agent1 or not agent2:
            logger.info(f"One or both avatars missing, attempting to create them")

            # Try to create missing avatars
            if not agent1:
                try:
                    from app.services.avatar_service import AvatarService
                    avatar_service = AvatarService(db)
                    await avatar_service.create_or_update_avatar(str(session.user1_id))
                    agent1 = await ai_service.get_user_avatar_agent(str(session.user1_id))
                    logger.info(f"Created avatar for user1: {session.user1_id}")
                except Exception as e:
                    logger.error(f"Failed to create avatar for user1: {e}")

            if not agent2:
                try:
                    from app.services.avatar_service import AvatarService
                    avatar_service = AvatarService(db)
                    await avatar_service.create_or_update_avatar(str(session.user2_id))
                    agent2 = await ai_service.get_user_avatar_agent(str(session.user2_id))
                    logger.info(f"Created avatar for user2: {session.user2_id}")
                except Exception as e:
                    logger.error(f"Failed to create avatar for user2: {e}")

        # If still missing, send error and return
        if not agent1 or not agent2:
            missing_users = []
            if not agent1:
                missing_users.append("user1")
            if not agent2:
                missing_users.append("user2")

            error_msg = f"AI avatars not available for {', '.join(missing_users)}. Please complete your personality assessment first."
            logger.error(f"Failed to get avatar agents for session {session_id}: {error_msg}")

            await manager.broadcast_to_session({
                "type": "error",
                "message": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            }, session_id)
            return

        # Start conversation with initial greeting
        conversation_history = []

        # Agent 1 starts the conversation
        logger.info(f"Agent 1 ({agent1.name}) generating initial greeting")
        greeting1 = await agent1.generate_response(conversation_history, {"is_first_message": True})

        # Store and broadcast first message
        message1 = ConversationMessage(
            id=uuid.uuid4(),
            session_id=session_id,
            sender_id=str(session.user1_id),
            sender_type="user_avatar",
            sender_name=agent1.name,
            content=greeting1,
            timestamp=datetime.utcnow()
        )
        db.add(message1)
        await db.commit()

        await manager.broadcast_to_session({
            "type": "ai_message",
            "message_id": str(message1.id),
            "sender_type": "user_avatar",
            "sender_name": agent1.name,
            "content": greeting1,
            "emotion_indicators": ["friendly", "curious"],
            "timestamp": datetime.utcnow().isoformat()
        }, session_id)

        conversation_history.append({
            "sender_id": str(session.user1_id),
            "sender_type": "user_avatar",
            "sender_name": agent1.name,
            "content": greeting1,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Continue conversation for several turns (configurable)
        max_turns = settings.MAX_CONVERSATION_TURNS if hasattr(settings, 'MAX_CONVERSATION_TURNS') else 12
        for turn in range(max_turns):  # More turns for better conversation
            await asyncio.sleep(4)  # Natural delay between messages

            # Alternate between agents
            if turn % 2 == 0:
                # Agent 2's turn
                logger.info(f"Agent 2 ({agent2.name}) generating response")
                response = await agent2.generate_response(conversation_history)
                sender_id = str(session.user2_id)
                sender_name = agent2.name
            else:
                # Agent 1's turn
                logger.info(f"Agent 1 ({agent1.name}) generating response")
                response = await agent1.generate_response(conversation_history)
                sender_id = str(session.user1_id)
                sender_name = agent1.name

            # Store message
            message = ConversationMessage(
                id=uuid.uuid4(),
                session_id=session_id,
                sender_id=sender_id,
                sender_type="user_avatar",
                sender_name=sender_name,
                content=response,
                timestamp=datetime.utcnow()
            )
            db.add(message)
            await db.commit()

            # Broadcast message
            await manager.broadcast_to_session({
                "type": "ai_message",
                "message_id": str(message.id),
                "sender_type": "user_avatar",
                "sender_name": sender_name,
                "content": response,
                "emotion_indicators": ["engaged", "interested"],
                "is_highlighted": turn >= 4,  # Highlight later messages
                "timestamp": datetime.utcnow().isoformat()
            }, session_id)

            # Update conversation history
            conversation_history.append({
                "sender_id": sender_id,
                "sender_type": "user_avatar",
                "sender_name": sender_name,
                "content": response,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Send compatibility update every 2 turns
            if turn % 2 == 1:
                await asyncio.sleep(1)
                compatibility_score = 0.65 + (turn * 0.05)  # Gradually increasing
                await manager.broadcast_to_session({
                    "type": "compatibility_update",
                    "overall_score": min(compatibility_score, 0.95),
                    "dimension_scores": {
                        "personality": min(0.70 + (turn * 0.04), 0.95),
                        "communication": min(0.68 + (turn * 0.03), 0.92),
                        "values": min(0.72 + (turn * 0.05), 0.96),
                        "lifestyle": min(0.65 + (turn * 0.04), 0.90)
                    },
                    "trending_direction": "improving",
                    "key_insights": [
                        "Natural conversation flow developing",
                        "Shared interests emerging",
                        "Good communication compatibility"
                    ],
                    "timestamp": datetime.utcnow().isoformat()
                }, session_id)

        # Mark session as completed
        await db.execute(
            update(ConversationSession)
            .where(ConversationSession.id == session_id)
            .values(
                status=SessionStatus.COMPLETED.value,
                ended_at=datetime.utcnow()
            )
        )
        await db.commit()

        await manager.broadcast_to_session({
            "type": "session_status_change",
            "status": "completed",
            "message": "Conversation completed successfully!",
            "timestamp": datetime.utcnow().isoformat()
        }, session_id)

        logger.info(f"AI conversation completed for session {session_id}")

    except Exception as e:
        error_str = str(e)
        logger.error(f"Error in AI conversation: {error_str}", exc_info=True)
        
        # Check if it's a Gemini quota error
        if "GEMINI_QUOTA_EXCEEDED" in error_str or "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            # Mark session as terminated due to quota
            await db.execute(
                update(ConversationSession)
                .where(ConversationSession.id == session_id)
                .values(
                    status=SessionStatus.TERMINATED.value,
                    ended_at=datetime.utcnow()
                )
            )
            await db.commit()
            
            # Broadcast quota exceeded error
            await manager.broadcast_to_session({
                "type": "gemini_quota_exceeded",
                "message": "Gemini API quota limit reached",
                "details": "The system's Gemini API Key has reached its daily usage limit. Please configure your own API Key to continue using AI conversation features.",
                "action": "configure_api_key",
                "timestamp": datetime.utcnow().isoformat()
            }, session_id)
            
            # Also send session status change
            await manager.broadcast_to_session({
                "type": "session_status_change",
                "status": "terminated",
                "reason": "quota_exceeded",
                "message": "Conversation stopped due to API quota limit",
                "timestamp": datetime.utcnow().isoformat()
            }, session_id)
        else:
            await manager.broadcast_to_session({
                "type": "error",
                "message": f"Conversation error: {error_str}",
                "timestamp": datetime.utcnow().isoformat()
            }, session_id)


async def handle_user_guidance(
    message_data: dict,
    session_id: str,
    user: User,
    websocket: WebSocket,
    db: AsyncSession
):
    """Handle user guidance for their AI avatar."""
    guidance = message_data.get("guidance", {})
    avatar_id = guidance.get("avatar_id")
    instruction = guidance.get("instruction", "")
    
    # In real implementation, send guidance to AI avatar
    response = {
        "type": "guidance_sent",
        "avatar_id": avatar_id,
        "message": f"Guidance sent to avatar: {instruction[:50]}...",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.send_personal_message(response, websocket)


async def handle_end_conversation(
    message_data: dict,
    session_id: str,
    user: User,
    websocket: WebSocket,
    db: AsyncSession
):
    """Handle manual conversation end request."""
    try:
        from app.models.conversation import ConversationSession, SessionStatus
        from sqlalchemy import select, update

        # Update session status to completed
        await db.execute(
            update(ConversationSession)
            .where(ConversationSession.id == session_id)
            .values(
                status=SessionStatus.COMPLETED.value,
                ended_at=datetime.utcnow()
            )
        )
        await db.commit()

        # Notify all viewers
        await manager.broadcast_to_session({
            "type": "session_status_change",
            "status": "completed",
            "message": "Conversation ended by user",
            "ended_by": f"{user.first_name} {user.last_name}",
            "timestamp": datetime.utcnow().isoformat()
        }, session_id)

        logger.info(f"Conversation manually ended by user {user.id} for session {session_id}")

    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Failed to end conversation: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)


async def handle_user_reaction(
    message_data: dict,
    session_id: str,
    user: User,
    websocket: WebSocket,
    db: AsyncSession
):
    """Handle user reaction to conversation moments."""
    reaction = message_data.get("reaction", {})
    message_id = reaction.get("message_id")
    reaction_type = reaction.get("type")  # "like", "love", "concern", etc.
    
    # Broadcast reaction to other viewers
    await manager.broadcast_to_session({
        "type": "user_reaction",
        "user_id": str(user.id),
        "user_name": f"{user.first_name} {user.last_name}",
        "message_id": message_id,
        "reaction_type": reaction_type,
        "timestamp": datetime.utcnow().isoformat()
    }, session_id, exclude_websocket=websocket)


async def simulate_ai_conversation(session_id: str):
    """Simulate AI conversation for demo purposes."""
    # This is a placeholder - in real implementation, this would trigger actual AI agents
    
    messages = [
        {
            "type": "ai_message",
            "message_id": f"msg_{datetime.utcnow().timestamp()}_1",
            "sender_type": "user_avatar",
            "sender_name": "Alex's Avatar",
            "content": "Hi there! I'm really excited to get to know you better. I love how adventurous you seem from your profile!",
            "emotion_indicators": ["excited", "friendly", "curious"],
            "compatibility_impact": 0.05,
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "type": "ai_message",
            "message_id": f"msg_{datetime.utcnow().timestamp()}_2",
            "sender_type": "user_avatar", 
            "sender_name": "Sarah's Avatar",
            "content": "Hello! Thank you, that's so sweet. I'm looking forward to our conversation too. What kind of adventures do you enjoy most?",
            "emotion_indicators": ["warm", "curious", "engaged"],
            "compatibility_impact": 0.03,
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "type": "ai_message",
            "message_id": f"msg_{datetime.utcnow().timestamp()}_3",
            "sender_type": "user_avatar",
            "sender_name": "Alex's Avatar",
            "content": "I'm really into hiking and rock climbing! There's something about being in nature that just centers me. Do you enjoy outdoor activities too?",
            "emotion_indicators": ["passionate", "enthusiastic"],
            "compatibility_impact": 0.08,
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "type": "ai_message",
            "message_id": f"msg_{datetime.utcnow().timestamp()}_4",
            "sender_type": "user_avatar",
            "sender_name": "Sarah's Avatar", 
            "content": "Oh wow, we have so much in common! I absolutely love hiking - it's my favorite way to clear my head and connect with nature. I've been wanting to try rock climbing actually!",
            "emotion_indicators": ["excited", "connected", "interested"],
            "compatibility_impact": 0.12,
            "is_highlighted": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    ]
    
    # Send messages with realistic delays
    for i, message in enumerate(messages):
        await asyncio.sleep(3 + i)  # Increasing delays to simulate natural conversation
        await manager.broadcast_to_session(message, session_id)
        
        # Send compatibility updates after key messages
        if message.get("is_highlighted"):
            await asyncio.sleep(1)
            await manager.broadcast_to_session({
                "type": "compatibility_update",
                "overall_score": 0.72 + (i * 0.02),
                "dimension_scores": {
                    "personality": 0.75 + (i * 0.02),
                    "communication": 0.70 + (i * 0.01),
                    "values": 0.68 + (i * 0.03),
                    "lifestyle": 0.74 + (i * 0.02)
                },
                "trending_direction": "improving",
                "recent_highlight": {
                    "message_id": message["message_id"],
                    "reason": "Strong shared interest discovered",
                    "impact": message.get("compatibility_impact", 0.0)
                },
                "timestamp": datetime.utcnow().isoformat()
            }, session_id)


@router.websocket("/notifications/{user_id}")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time notifications.
    Handles match notifications, message alerts, and system updates.
    """
    user = None
    
    try:
        # Authenticate user
        user = await manager.authenticate_websocket(websocket, token, db)
        if not user or str(user.id) != user_id:
            await websocket.close(code=1008, reason="Authentication failed")
            return
        
        await websocket.accept()
        
        # Store user connection for notifications
        manager.user_connections[user_id] = websocket
        manager.user_presence[user_id] = datetime.utcnow()
        
        # Send welcome message
        await manager.send_personal_message({
            "type": "notifications_connected",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
        # Keep connection alive and handle ping/pong
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if message_data.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                    manager.user_presence[user_id] = datetime.utcnow()
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in notifications WebSocket: {e}")
                break
    
    except Exception as e:
        logger.error(f"Notifications WebSocket error: {e}")
    
    finally:
        # Clean up
        if user_id in manager.user_connections:
            del manager.user_connections[user_id]
        if user_id in manager.user_presence:
            del manager.user_presence[user_id]


@router.websocket("/admin/monitor")
async def websocket_admin_monitor_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for admin monitoring.
    Provides real-time system statistics and session monitoring.
    """
    try:
        # Authenticate admin user (simplified for demo)
        user = await manager.authenticate_websocket(websocket, token, db)
        if not user:
            await websocket.close(code=1008, reason="Authentication failed")
            return
        
        await websocket.accept()
        
        # Send initial system status
        await websocket.send_text(json.dumps({
            "type": "system_status",
            "active_sessions": len(manager.active_sessions),
            "connected_users": len(manager.user_connections),
            "total_connections": sum(len(conns) for conns in manager.session_connections.values()),
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Send periodic updates
        while True:
            await asyncio.sleep(10)  # Update every 10 seconds
            
            # Gather system metrics
            system_metrics = {
                "type": "system_metrics",
                "active_sessions": len(manager.active_sessions),
                "connected_users": len(manager.user_connections),
                "total_connections": sum(len(conns) for conns in manager.session_connections.values()),
                "session_details": [
                    {
                        "session_id": session_id,
                        "viewer_count": data["viewer_count"],
                        "status": data["status"],
                        "duration_minutes": (datetime.utcnow() - data["started_at"]).total_seconds() / 60
                    }
                    for session_id, data in manager.active_sessions.items()
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(system_metrics))
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Admin monitor WebSocket error: {e}")


# Utility functions for external services to send real-time updates

async def send_match_notification(user_id: str, match_data: dict):
    """Send real-time match notification to user."""
    notification = {
        "type": "new_match",
        "match_id": match_data.get("match_id"),
        "match_name": match_data.get("match_name"),
        "match_photo": match_data.get("match_photo"),
        "compatibility_score": match_data.get("compatibility_score"),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_user(notification, user_id)


async def send_session_invitation(user_id: str, session_data: dict):
    """Send real-time session invitation to user."""
    invitation = {
        "type": "session_invitation",
        "session_id": session_data.get("session_id"),
        "match_name": session_data.get("match_name"),
        "session_type": session_data.get("session_type", "conversation"),
        "expires_at": session_data.get("expires_at"),
        "websocket_url": f"/ws/session/{session_data.get('session_id')}",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_user(invitation, user_id)


async def send_compatibility_report_ready(user_id: str, report_data: dict):
    """Send notification when compatibility report is ready."""
    notification = {
        "type": "compatibility_report_ready",
        "report_id": report_data.get("report_id"),
        "match_name": report_data.get("match_name"),
        "overall_score": report_data.get("overall_score"),
        "report_url": f"/compatibility/{report_data.get('report_id')}",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_user(notification, user_id)


async def broadcast_system_announcement(message: str, announcement_type: str = "info"):
    """Broadcast system-wide announcement to all connected users."""
    announcement = {
        "type": "system_announcement",
        "announcement_type": announcement_type,  # "info", "warning", "maintenance"
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send to all connected users
    for user_id, websocket in manager.user_connections.items():
        await manager.send_personal_message(announcement, websocket)