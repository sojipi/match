"""
Conversation and message data models.

Contains data classes for conversation sessions, messages, and communication.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from .enums import AgentType, SessionType, SessionStatus


class Message(BaseModel):
    """Individual message in a conversation."""
    
    message_id: str = Field(description="Unique message identifier")
    sender_id: str = Field(description="ID of the message sender")
    sender_type: AgentType = Field(description="Type of agent that sent the message")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional message metadata"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "sender_type": self.sender_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(
            message_id=data["message_id"],
            sender_id=data["sender_id"],
            sender_type=AgentType(data["sender_type"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


class ConversationSession(BaseModel):
    """A conversation session between agents."""
    
    session_id: str = Field(description="Unique session identifier")
    participants: List[str] = Field(description="List of participant user IDs")
    session_type: SessionType = Field(description="Type of conversation session")
    messages: List[Message] = Field(
        default_factory=list,
        description="Messages in the conversation"
    )
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: SessionStatus = SessionStatus.ACTIVE
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Session metadata and configuration"
    )
    
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
    
    def get_messages_by_sender(self, sender_id: str) -> List[Message]:
        """Get all messages from a specific sender."""
        return [msg for msg in self.messages if msg.sender_id == sender_id]
    
    def get_messages_by_type(self, sender_type: AgentType) -> List[Message]:
        """Get all messages from a specific agent type."""
        return [msg for msg in self.messages if msg.sender_type == sender_type]
    
    def get_duration(self) -> Optional[float]:
        """Get session duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def end_session(self) -> None:
        """Mark the session as completed."""
        self.end_time = datetime.utcnow()
        self.status = SessionStatus.COMPLETED
    
    def terminate_session(self) -> None:
        """Mark the session as terminated."""
        self.end_time = datetime.utcnow()
        self.status = SessionStatus.TERMINATED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "participants": self.participants,
            "session_type": self.session_type.value,
            "messages": [msg.to_dict() for msg in self.messages],
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status.value,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSession':
        """Create session from dictionary."""
        messages = [Message.from_dict(msg_data) for msg_data in data.get("messages", [])]
        end_time = None
        if data.get("end_time"):
            end_time = datetime.fromisoformat(data["end_time"])
            
        return cls(
            session_id=data["session_id"],
            participants=data["participants"],
            session_type=SessionType(data["session_type"]),
            messages=messages,
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=end_time,
            status=SessionStatus(data["status"]),
            metadata=data.get("metadata", {})
        )


class InteractionAnalysis(BaseModel):
    """Analysis of interaction patterns between participants."""
    
    communication_patterns: Dict[str, Any] = Field(
        default_factory=dict,
        description="Analysis of communication styles and patterns"
    )
    conflict_instances: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Recorded instances of conflict or disagreement"
    )
    collaboration_examples: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Examples of successful collaboration"
    )
    response_times: Dict[str, float] = Field(
        default_factory=dict,
        description="Average response times by participant"
    )
    engagement_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Engagement and participation metrics"
    )


class ConversationSummary(BaseModel):
    """Summary of a completed conversation session."""
    
    session_id: str = Field(description="Session identifier")
    participants: List[str] = Field(description="Participant user IDs")
    duration: float = Field(description="Session duration in seconds")
    message_count: int = Field(description="Total number of messages")
    key_topics: List[str] = Field(
        default_factory=list,
        description="Key topics discussed"
    )
    interaction_analysis: InteractionAnalysis
    compatibility_indicators: Dict[str, float] = Field(
        default_factory=dict,
        description="Preliminary compatibility indicators"
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_session(cls, session: ConversationSession) -> 'ConversationSummary':
        """Create summary from a conversation session."""
        duration = session.get_duration() or 0.0
        
        # Basic interaction analysis
        interaction_analysis = InteractionAnalysis()
        
        # Calculate basic metrics
        participant_message_counts = {}
        for participant in session.participants:
            participant_messages = session.get_messages_by_sender(participant)
            participant_message_counts[participant] = len(participant_messages)
        
        interaction_analysis.engagement_metrics = {
            "message_counts": participant_message_counts,
            "total_messages": len(session.messages)
        }
        
        return cls(
            session_id=session.session_id,
            participants=session.participants,
            duration=duration,
            message_count=len(session.messages),
            interaction_analysis=interaction_analysis
        )