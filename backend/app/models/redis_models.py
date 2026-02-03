"""
Redis models for caching and real-time data.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json
import redis
import uuid
from app.core.config import settings


# Redis client instance with timeout settings to prevent blocking
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,  # 5 seconds to establish connection
    socket_timeout=5,  # 5 seconds for socket operations
    retry_on_timeout=True,  # Retry on timeout
    health_check_interval=30  # Health check every 30 seconds
)


class RedisBaseModel(BaseModel):
    """Base class for Redis models."""
    
    def to_redis_key(self, prefix: str, identifier: str) -> str:
        """Generate Redis key with prefix and identifier."""
        return f"{prefix}:{identifier}"
    
    def save_to_redis(self, key: str, ttl: Optional[int] = None) -> bool:
        """Save model to Redis with optional TTL."""
        try:
            data = self.model_dump_json()
            if ttl:
                redis_client.setex(key, ttl, data)
            else:
                redis_client.set(key, data)
            return True
        except Exception:
            return False
    
    @classmethod
    def load_from_redis(cls, key: str):
        """Load model from Redis."""
        try:
            data = redis_client.get(key)
            if data:
                return cls.model_validate_json(data)
            return None
        except Exception:
            return None
    
    def delete_from_redis(self, key: str) -> bool:
        """Delete model from Redis."""
        try:
            redis_client.delete(key)
            return True
        except Exception:
            return False


class UserSession(RedisBaseModel):
    """User session data stored in Redis."""
    
    user_id: str
    session_token: str
    refresh_token: str
    device_info: Dict[str, Any] = Field(default_factory=dict)
    ip_address: str
    user_agent: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    
    def save_session(self) -> bool:
        """Save session to Redis with TTL."""
        key = self.to_redis_key("session", self.session_token)
        ttl = int((self.expires_at - datetime.utcnow()).total_seconds())
        return self.save_to_redis(key, ttl)
    
    @classmethod
    def get_session(cls, session_token: str) -> Optional['UserSession']:
        """Get session from Redis."""
        key = f"session:{session_token}"
        return cls.load_from_redis(key)
    
    def delete_session(self) -> bool:
        """Delete session from Redis."""
        key = self.to_redis_key("session", self.session_token)
        return self.delete_from_redis(key)


class LiveSessionData(RedisBaseModel):
    """Live session data for real-time updates."""
    
    session_id: str
    user1_id: str
    user2_id: str
    status: str  # waiting, active, completed, terminated
    connected_users: List[str] = Field(default_factory=list)
    viewer_count: int = 0
    current_compatibility_score: float = 0.0
    last_message_id: Optional[str] = None
    last_update: datetime = Field(default_factory=datetime.utcnow)
    
    def save_live_session(self) -> bool:
        """Save live session data to Redis."""
        key = self.to_redis_key("live_session", self.session_id)
        # Live sessions expire after 24 hours of inactivity
        ttl = 24 * 60 * 60
        return self.save_to_redis(key, ttl)
    
    @classmethod
    def get_live_session(cls, session_id: str) -> Optional['LiveSessionData']:
        """Get live session data from Redis."""
        key = f"live_session:{session_id}"
        return cls.load_from_redis(key)
    
    def add_connected_user(self, user_id: str) -> bool:
        """Add user to connected users list."""
        if user_id not in self.connected_users:
            self.connected_users.append(user_id)
            self.viewer_count = len(self.connected_users)
            self.last_update = datetime.utcnow()
            return self.save_live_session()
        return True
    
    def remove_connected_user(self, user_id: str) -> bool:
        """Remove user from connected users list."""
        if user_id in self.connected_users:
            self.connected_users.remove(user_id)
            self.viewer_count = len(self.connected_users)
            self.last_update = datetime.utcnow()
            return self.save_live_session()
        return True


class UserOnlineStatus(RedisBaseModel):
    """User online status tracking."""
    
    user_id: str
    is_online: bool = True
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    current_activity: str = "browsing"  # browsing, in_session, away
    device_type: str = "web"  # web, mobile, tablet
    
    def save_online_status(self) -> bool:
        """Save online status to Redis."""
        key = self.to_redis_key("online", self.user_id)
        # Online status expires after 5 minutes of inactivity
        ttl = 5 * 60
        return self.save_to_redis(key, ttl)
    
    @classmethod
    def get_online_status(cls, user_id: str) -> Optional['UserOnlineStatus']:
        """Get user online status from Redis."""
        key = f"online:{user_id}"
        return cls.load_from_redis(key)
    
    def update_activity(self, activity: str) -> bool:
        """Update user activity."""
        self.current_activity = activity
        self.last_seen = datetime.utcnow()
        return self.save_online_status()


class MatchingQueue(RedisBaseModel):
    """Matching queue for users looking for matches."""
    
    user_id: str
    preferences: Dict[str, Any] = Field(default_factory=dict)
    personality_vector: List[float] = Field(default_factory=list)
    location: Dict[str, Any] = Field(default_factory=dict)
    queue_priority: int = 1  # 1=normal, 2=premium, 3=super_premium
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    def join_queue(self) -> bool:
        """Add user to matching queue."""
        key = self.to_redis_key("queue", self.user_id)
        # Queue entries expire after 1 hour
        ttl = 60 * 60
        return self.save_to_redis(key, ttl)
    
    @classmethod
    def get_queue_entry(cls, user_id: str) -> Optional['MatchingQueue']:
        """Get user's queue entry."""
        key = f"queue:{user_id}"
        return cls.load_from_redis(key)
    
    def leave_queue(self) -> bool:
        """Remove user from matching queue."""
        key = self.to_redis_key("queue", self.user_id)
        return self.delete_from_redis(key)
    
    @classmethod
    def get_all_queue_entries(cls) -> List['MatchingQueue']:
        """Get all users in matching queue."""
        pattern = "queue:*"
        keys = redis_client.keys(pattern)
        entries = []
        for key in keys:
            entry = cls.load_from_redis(key)
            if entry:
                entries.append(entry)
        return sorted(entries, key=lambda x: (x.queue_priority, x.joined_at), reverse=True)


class RealtimeUpdate(RedisBaseModel):
    """Real-time update message for WebSocket broadcasting."""
    
    update_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    update_type: str  # message, compatibility, status, user_action
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    target_users: List[str] = Field(default_factory=list)  # Empty means broadcast to all session users
    
    def publish_update(self) -> bool:
        """Publish update to Redis pub/sub channel."""
        try:
            channel = f"session_updates:{self.session_id}"
            message = self.model_dump_json()
            redis_client.publish(channel, message)
            return True
        except Exception:
            return False
    
    @classmethod
    def subscribe_to_session(cls, session_id: str):
        """Subscribe to session updates."""
        channel = f"session_updates:{session_id}"
        pubsub = redis_client.pubsub()
        pubsub.subscribe(channel)
        return pubsub


class CachedCompatibilityScore(RedisBaseModel):
    """Cached compatibility score between users."""
    
    user1_id: str
    user2_id: str
    compatibility_score: float
    dimension_scores: Dict[str, float] = Field(default_factory=dict)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def save_score(self) -> bool:
        """Save compatibility score to Redis."""
        # Create bidirectional keys for easy lookup
        key1 = self.to_redis_key("compat", f"{self.user1_id}:{self.user2_id}")
        key2 = self.to_redis_key("compat", f"{self.user2_id}:{self.user1_id}")
        # Cache compatibility scores for 24 hours
        ttl = 24 * 60 * 60
        success1 = self.save_to_redis(key1, ttl)
        success2 = self.save_to_redis(key2, ttl)
        return success1 and success2
    
    @classmethod
    def get_score(cls, user1_id: str, user2_id: str) -> Optional['CachedCompatibilityScore']:
        """Get cached compatibility score."""
        key = f"compat:{user1_id}:{user2_id}"
        return cls.load_from_redis(key)


# Utility functions for Redis operations
def clear_user_cache(user_id: str) -> bool:
    """Clear all cached data for a user."""
    try:
        patterns = [
            f"session:*",  # Will need to check session content
            f"online:{user_id}",
            f"queue:{user_id}",
            f"compat:{user_id}:*",
            f"compat:*:{user_id}"
        ]
        
        keys_to_delete = []
        for pattern in patterns:
            keys_to_delete.extend(redis_client.keys(pattern))
        
        if keys_to_delete:
            redis_client.delete(*keys_to_delete)
        
        return True
    except Exception:
        return False


def get_active_sessions_count() -> int:
    """Get count of active live sessions."""
    try:
        pattern = "live_session:*"
        keys = redis_client.keys(pattern)
        return len(keys)
    except Exception:
        return 0


def get_online_users_count() -> int:
    """Get count of online users."""
    try:
        pattern = "online:*"
        keys = redis_client.keys(pattern)
        return len(keys)
    except Exception:
        return 0