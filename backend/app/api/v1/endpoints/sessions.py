"""
AI matching session endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.conversation import ConversationSession, SessionStatus
from app.models.match import Match
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


class SessionCreate(BaseModel):
    """Session creation request."""
    match_id: str
    session_type: str = "conversation"


class SessionResponse(BaseModel):
    """Session response."""
    session_id: str
    match_id: str
    status: str
    session_type: str
    start_time: Optional[datetime] = None
    live_compatibility_score: float = 0.0


class ConversationMessage(BaseModel):
    """Conversation message."""
    message_id: str
    sender_type: str
    sender_name: str
    content: str
    timestamp: datetime
    emotion_indicators: List[str] = []


@router.post("/create", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new AI matching session."""
    try:
        # Verify match exists and user has access
        result = await db.execute(
            select(Match).where(Match.id == session_data.match_id)
        )
        match = result.scalar_one_or_none()

        if not match:
            raise HTTPException(status_code=404, detail="Match not found")

        # Verify user is part of this match
        if str(match.user1_id) != str(current_user.id) and str(match.user2_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied to this match")

        # Create new conversation session
        session = ConversationSession(
            id=uuid.uuid4(),
            user1_id=match.user1_id,
            user2_id=match.user2_id,
            session_type=session_data.session_type,
            status=SessionStatus.WAITING.value
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        return SessionResponse(
            session_id=str(session.id),
            match_id=str(match.id),
            status=session.status,
            session_type=session.session_type,
            start_time=session.created_at,
            live_compatibility_score=0.0
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get session details."""
    # This is a placeholder - implement actual session retrieval
    return SessionResponse(
        session_id=session_id,
        match_id="match-123",
        status="active",
        session_type="conversation",
        start_time=datetime.utcnow(),
        live_compatibility_score=0.75
    )


@router.post("/{session_id}/start")
async def start_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Start an AI matching session."""
    # This is a placeholder - implement actual session start
    return {"message": f"Session {session_id} started", "websocket_url": f"/ws/session/{session_id}"}


@router.post("/{session_id}/end")
async def end_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """End an AI matching session."""
    # This is a placeholder - implement actual session end
    return {
        "message": f"Session {session_id} ended",
        "final_compatibility_score": 0.82,
        "report_id": "report-456"
    }


@router.get("/match/{match_id}/sessions")
async def get_match_sessions(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all conversation sessions for a match."""
    from app.models.conversation import ConversationSession as DBConversationSession
    from sqlalchemy import or_, and_, desc
    
    try:
        # Verify match exists and user has access
        result = await db.execute(
            select(Match).where(Match.id == match_id)
        )
        match = result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Verify user is part of this match
        if str(match.user1_id) != str(current_user.id) and str(match.user2_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied to this match")
        
        # Get all sessions for this match
        sessions_result = await db.execute(
            select(DBConversationSession)
            .where(
                and_(
                    or_(
                        and_(
                            DBConversationSession.user1_id == match.user1_id,
                            DBConversationSession.user2_id == match.user2_id
                        ),
                        and_(
                            DBConversationSession.user1_id == match.user2_id,
                            DBConversationSession.user2_id == match.user1_id
                        )
                    )
                )
            )
            .order_by(desc(DBConversationSession.created_at))
        )
        sessions = sessions_result.scalars().all()
        
        return {
            "match_id": match_id,
            "sessions": [
                {
                    "session_id": str(session.id),
                    "status": session.status,
                    "session_type": session.session_type,
                    "started_at": session.started_at.isoformat() if session.started_at else None,
                    "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                    "message_count": session.message_count or 0,
                    "created_at": session.created_at.isoformat()
                }
                for session in sessions
            ],
            "total_count": len(sessions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")


@router.get("/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get session conversation messages."""
    from app.models.conversation import ConversationMessage as DBConversationMessage
    from sqlalchemy import desc
    
    try:
        # Verify session exists and user has access
        session_result = await db.execute(
            select(ConversationSession).where(ConversationSession.id == session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify user is part of this session
        if str(session.user1_id) != str(current_user.id) and str(session.user2_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied to this session")
        
        # Get total count
        count_result = await db.execute(
            select(DBConversationMessage).where(DBConversationMessage.session_id == session_id)
        )
        total_count = len(count_result.scalars().all())
        
        # Get messages with pagination
        messages_result = await db.execute(
            select(DBConversationMessage)
            .where(DBConversationMessage.session_id == session_id)
            .order_by(DBConversationMessage.timestamp)
            .offset(offset)
            .limit(limit)
        )
        messages = messages_result.scalars().all()
        
        # Convert to response format
        message_list = [
            ConversationMessage(
                message_id=str(msg.id),
                sender_type=msg.sender_type,
                sender_name=msg.sender_name,
                content=msg.content,
                timestamp=msg.timestamp,
                emotion_indicators=msg.emotion_indicators or []
            )
            for msg in messages
        ]
        
        return {
            "messages": message_list,
            "total_count": total_count,
            "has_more": offset + limit < total_count,
            "session": {
                "session_id": str(session.id),
                "status": session.status,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "ended_at": session.ended_at.isoformat() if session.ended_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")