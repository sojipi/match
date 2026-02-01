"""
AI matching session endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db

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
    db: AsyncSession = Depends(get_db)
):
    """Create a new AI matching session."""
    # This is a placeholder - implement actual session creation
    return SessionResponse(
        session_id="session-123",
        match_id=session_data.match_id,
        status="waiting",
        session_type=session_data.session_type,
        live_compatibility_score=0.0
    )


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


@router.get("/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get session conversation messages."""
    # This is a placeholder - implement actual message retrieval
    mock_messages = [
        ConversationMessage(
            message_id=f"msg-{i}",
            sender_type="user_avatar",
            sender_name="Alex's Avatar",
            content=f"This is message {i}",
            timestamp=datetime.utcnow(),
            emotion_indicators=["friendly", "curious"]
        )
        for i in range(1, 6)
    ]
    
    return {
        "messages": mock_messages[offset:offset + limit],
        "total_count": len(mock_messages),
        "has_more": offset + limit < len(mock_messages)
    }