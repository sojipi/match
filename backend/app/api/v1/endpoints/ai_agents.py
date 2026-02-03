"""
AI Agents API endpoints.
"""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.services.ai_agent_service import AIAgentService
from app.services.conversation_orchestration_service import ConversationOrchestrationService
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class StartConversationRequest(BaseModel):
    """Request to start a conversation session."""
    user2_id: str
    session_type: str = "matchmaking"
    max_duration_minutes: int = 60


class StartConversationResponse(BaseModel):
    """Response for starting a conversation session."""
    session_id: str
    status: str
    message: str


class SendMessageRequest(BaseModel):
    """Request to send a message in a conversation."""
    message_content: str


class SendMessageResponse(BaseModel):
    """Response for sending a message."""
    success: bool
    ai_response: Optional[str] = None
    facilitation_message: Optional[str] = None
    compatibility_update: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class GenerateScenarioRequest(BaseModel):
    """Request to generate a relationship scenario."""
    scenario_type: str = "general"


class GenerateScenarioResponse(BaseModel):
    """Response for generating a scenario."""
    scenario: Dict[str, Any]


class ConversationHistoryResponse(BaseModel):
    """Response for conversation history."""
    messages: List[Dict[str, Any]]
    session_info: Dict[str, Any]


class CompatibilityReportResponse(BaseModel):
    """Response for compatibility report."""
    report: Dict[str, Any]


# AI Agent Endpoints
@router.post("/conversations/start", response_model=StartConversationResponse)
async def start_conversation(
    request: StartConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a new AI conversation session between two users."""
    try:
        orchestration_service = ConversationOrchestrationService(db)
        
        session_id = await orchestration_service.start_conversation_session(
            user1_id=str(current_user.id),
            user2_id=request.user2_id,
            session_type=request.session_type,
            max_duration_minutes=request.max_duration_minutes
        )
        
        return StartConversationResponse(
            session_id=session_id,
            status="started",
            message="Conversation session started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message in a conversation session and get AI response."""
    try:
        orchestration_service = ConversationOrchestrationService(db)
        
        result = await orchestration_service.process_user_message(
            session_id=session_id,
            user_id=str(current_user.id),
            message_content=request.message_content
        )
        
        return SendMessageResponse(**result)
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{session_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get conversation history for a session."""
    try:
        orchestration_service = ConversationOrchestrationService(db)
        
        # Get conversation history
        conversation_history = await orchestration_service._get_conversation_history(session_id)
        
        # Get session info
        session_info = orchestration_service.active_sessions.get(session_id, {})
        
        return ConversationHistoryResponse(
            messages=conversation_history,
            session_info=session_info
        )
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{session_id}/scenarios", response_model=GenerateScenarioResponse)
async def generate_scenario(
    session_id: str,
    request: GenerateScenarioRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a relationship scenario for the conversation session."""
    try:
        ai_agent_service = AIAgentService(db)
        
        scenario = await ai_agent_service.generate_scenario(
            session_id=session_id,
            scenario_type=request.scenario_type
        )
        
        return GenerateScenarioResponse(scenario=scenario)
        
    except Exception as e:
        logger.error(f"Error generating scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{session_id}/end")
async def end_conversation(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """End a conversation session and generate final report."""
    try:
        orchestration_service = ConversationOrchestrationService(db)
        
        result = await orchestration_service.end_conversation_session(
            session_id=session_id,
            reason="user_request"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{session_id}/compatibility", response_model=CompatibilityReportResponse)
async def get_compatibility_report(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get compatibility report for a conversation session."""
    try:
        from sqlalchemy import select
        from app.models.conversation import ConversationCompatibilityReport
        
        # Get the latest compatibility report for the session
        result = await db.execute(
            select(ConversationCompatibilityReport)
            .where(ConversationCompatibilityReport.session_id == session_id)
            .order_by(ConversationCompatibilityReport.generated_at.desc())
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(status_code=404, detail="Compatibility report not found")
        
        report_data = {
            "report_id": str(report.id),
            "session_id": str(report.session_id),
            "overall_score": report.overall_score,
            "dimension_scores": {
                "personality_compatibility": report.personality_compatibility,
                "communication_style": report.communication_style,
                "emotional_connection": report.emotional_connection,
                "conversation_quality": report.conversation_quality
            },
            "strengths": report.strengths,
            "challenges": report.challenges,
            "recommendations": report.recommendations,
            "conversation_highlights": report.conversation_highlights,
            "generated_at": report.generated_at.isoformat(),
            "is_final": report.is_final
        }
        
        return CompatibilityReportResponse(report=report_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting compatibility report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Avatar Management Endpoints
@router.get("/avatars/me")
async def get_my_avatar(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's AI avatar information."""
    try:
        ai_agent_service = AIAgentService(db)
        
        avatar_agent = await ai_agent_service.get_user_avatar_agent(str(current_user.id))
        
        if not avatar_agent:
            raise HTTPException(status_code=404, detail="Avatar not found")
        
        return {
            "avatar_id": str(avatar_agent.avatar.id),
            "name": avatar_agent.name,
            "personality_config": avatar_agent.personality_config,
            "status": avatar_agent.avatar.status,
            "completeness_score": avatar_agent.avatar.completeness_score,
            "authenticity_score": avatar_agent.avatar.authenticity_score,
            "consistency_score": avatar_agent.avatar.consistency_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting avatar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/avatars/me/test-response")
async def test_avatar_response(
    message: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test avatar response generation."""
    try:
        ai_agent_service = AIAgentService(db)
        
        avatar_agent = await ai_agent_service.get_user_avatar_agent(str(current_user.id))
        
        if not avatar_agent:
            raise HTTPException(status_code=404, detail="Avatar not found")
        
        # Create a simple conversation history for testing
        test_conversation = [
            {
                "sender_id": "test_user",
                "sender_type": "user",
                "sender_name": "Test User",
                "content": message,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        ]
        
        response = await avatar_agent.generate_response(test_conversation)
        
        return {
            "user_message": message,
            "avatar_response": response,
            "avatar_name": avatar_agent.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing avatar response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time conversation updates
@router.websocket("/conversations/{session_id}/ws")
async def conversation_websocket(
    websocket: WebSocket,
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time conversation updates."""
    await websocket.accept()
    
    orchestration_service = ConversationOrchestrationService(db)
    
    try:
        # Add WebSocket connection
        await orchestration_service.add_websocket_connection(session_id, websocket)
        
        # Send initial session status
        await websocket.send_json({
            "type": "connection_established",
            "session_id": session_id,
            "timestamp": "2024-01-01T00:00:00Z"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_json()
                
                # Handle different message types
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data.get("type") == "user_message":
                    # This would typically be handled by the REST API
                    # but we can also handle it here for real-time processing
                    pass
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket communication: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        # Clean up WebSocket connection
        await orchestration_service.remove_websocket_connection(session_id, websocket)


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for AI agent services."""
    try:
        # Check if required services are available
        health_status = {
            "status": "healthy",
            "services": {
                "agentscope": "available" if hasattr(AIAgentService, 'AGENTSCOPE_AVAILABLE') else "unavailable",
                "gemini_api": "configured" if hasattr(AIAgentService, 'GEMINI_AVAILABLE') else "not_configured"
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")