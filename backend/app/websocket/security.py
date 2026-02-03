"""
WebSocket security and authentication utilities.
"""
import time
import logging
from typing import Dict, Optional, Set, Tuple, List
from datetime import datetime, timedelta
from collections import defaultdict, deque

from fastapi import WebSocket, HTTPException
from app.core.security import verify_token

logger = logging.getLogger(__name__)


class WebSocketRateLimiter:
    """
    Rate limiter for WebSocket connections to prevent abuse.
    Implements sliding window rate limiting per user and per IP.
    """
    
    def __init__(
        self,
        max_connections_per_user: int = 5,
        max_connections_per_ip: int = 20,
        max_messages_per_minute: int = 60,
        max_messages_per_hour: int = 1000
    ):
        self.max_connections_per_user = max_connections_per_user
        self.max_connections_per_ip = max_connections_per_ip
        self.max_messages_per_minute = max_messages_per_minute
        self.max_messages_per_hour = max_messages_per_hour
        
        # Connection tracking
        self.user_connections: Dict[str, int] = defaultdict(int)
        self.ip_connections: Dict[str, int] = defaultdict(int)
        
        # Message rate tracking (sliding window)
        self.user_messages: Dict[str, deque] = defaultdict(lambda: deque())
        self.ip_messages: Dict[str, deque] = defaultdict(lambda: deque())
        
        # Blocked users and IPs
        self.blocked_users: Dict[str, datetime] = {}
        self.blocked_ips: Dict[str, datetime] = {}
    
    def can_connect(self, user_id: str, client_ip: str) -> Tuple[bool, str]:
        """Check if a user/IP can establish a new WebSocket connection."""
        current_time = datetime.utcnow()
        
        # Check if user is blocked
        if user_id in self.blocked_users:
            if current_time < self.blocked_users[user_id]:
                return False, "User temporarily blocked due to rate limiting"
            else:
                del self.blocked_users[user_id]
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            if current_time < self.blocked_ips[client_ip]:
                return False, "IP temporarily blocked due to rate limiting"
            else:
                del self.blocked_ips[client_ip]
        
        # Check connection limits
        if self.user_connections[user_id] >= self.max_connections_per_user:
            return False, f"Maximum connections per user exceeded ({self.max_connections_per_user})"
        
        if self.ip_connections[client_ip] >= self.max_connections_per_ip:
            return False, f"Maximum connections per IP exceeded ({self.max_connections_per_ip})"
        
        return True, "Connection allowed"
    
    def add_connection(self, user_id: str, client_ip: str):
        """Register a new connection."""
        self.user_connections[user_id] += 1
        self.ip_connections[client_ip] += 1
        logger.info(f"Connection added - User: {user_id}, IP: {client_ip}")
    
    def remove_connection(self, user_id: str, client_ip: str):
        """Remove a connection."""
        if self.user_connections[user_id] > 0:
            self.user_connections[user_id] -= 1
        if self.ip_connections[client_ip] > 0:
            self.ip_connections[client_ip] -= 1
        
        # Clean up empty entries
        if self.user_connections[user_id] == 0:
            del self.user_connections[user_id]
        if self.ip_connections[client_ip] == 0:
            del self.ip_connections[client_ip]
        
        logger.info(f"Connection removed - User: {user_id}, IP: {client_ip}")
    
    def can_send_message(self, user_id: str, client_ip: str) -> Tuple[bool, str]:
        """Check if a user/IP can send a message."""
        current_time = time.time()
        
        # Clean old messages (sliding window)
        self._clean_old_messages(user_id, client_ip, current_time)
        
        # Check user message rate
        user_messages_minute = sum(
            1 for msg_time in self.user_messages[user_id]
            if current_time - msg_time <= 60
        )
        user_messages_hour = len(self.user_messages[user_id])
        
        if user_messages_minute >= self.max_messages_per_minute:
            # Block user for 1 minute
            self.blocked_users[user_id] = datetime.utcnow() + timedelta(minutes=1)
            return False, "Message rate limit exceeded (per minute)"
        
        if user_messages_hour >= self.max_messages_per_hour:
            # Block user for 1 hour
            self.blocked_users[user_id] = datetime.utcnow() + timedelta(hours=1)
            return False, "Message rate limit exceeded (per hour)"
        
        # Check IP message rate
        ip_messages_minute = sum(
            1 for msg_time in self.ip_messages[client_ip]
            if current_time - msg_time <= 60
        )
        
        if ip_messages_minute >= self.max_messages_per_minute * 2:  # More lenient for IP
            # Block IP for 5 minutes
            self.blocked_ips[client_ip] = datetime.utcnow() + timedelta(minutes=5)
            return False, "IP message rate limit exceeded"
        
        return True, "Message allowed"
    
    def record_message(self, user_id: str, client_ip: str):
        """Record a message for rate limiting."""
        current_time = time.time()
        
        self.user_messages[user_id].append(current_time)
        self.ip_messages[client_ip].append(current_time)
    
    def _clean_old_messages(self, user_id: str, client_ip: str, current_time: float):
        """Clean old messages outside the sliding window."""
        # Keep only messages from the last hour
        hour_ago = current_time - 3600
        
        # Clean user messages
        while (self.user_messages[user_id] and 
               self.user_messages[user_id][0] < hour_ago):
            self.user_messages[user_id].popleft()
        
        # Clean IP messages
        while (self.ip_messages[client_ip] and 
               self.ip_messages[client_ip][0] < hour_ago):
            self.ip_messages[client_ip].popleft()
    
    def get_stats(self) -> Dict:
        """Get current rate limiter statistics."""
        return {
            "active_user_connections": dict(self.user_connections),
            "active_ip_connections": dict(self.ip_connections),
            "blocked_users": len(self.blocked_users),
            "blocked_ips": len(self.blocked_ips),
            "total_connections": sum(self.user_connections.values())
        }


class WebSocketAuthenticator:
    """
    WebSocket authentication and authorization handler.
    Manages JWT token validation and user permissions.
    """
    
    def __init__(self):
        self.authenticated_connections: Dict[WebSocket, Dict] = {}
        self.user_permissions: Dict[str, Set[str]] = defaultdict(set)
    
    async def authenticate_connection(
        self, 
        websocket: WebSocket, 
        token: str,
        required_permissions: Set[str] = None
    ) -> Optional[Dict]:
        """
        Authenticate a WebSocket connection using JWT token.
        Returns user info if successful, None if failed.
        """
        try:
            # Verify JWT token
            payload = verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                logger.warning("JWT token missing user ID")
                return None
            
            # Extract user information
            # Default permissions to ["websocket_access"] for backward compatibility with old tokens
            permissions = payload.get("permissions", ["websocket_access"])
            
            user_info = {
                "user_id": user_id,
                "email": payload.get("email"),
                "username": payload.get("username"),
                "roles": payload.get("roles", []),
                "permissions": permissions,
                "authenticated_at": datetime.utcnow()
            }
            
            # Check required permissions
            if required_permissions:
                user_perms = set(user_info["permissions"])
                if not required_permissions.issubset(user_perms):
                    logger.warning(f"User {user_id} lacks required permissions: {required_permissions}")
                    return None
            
            # Store authentication info
            self.authenticated_connections[websocket] = user_info
            self.user_permissions[user_id] = set(user_info["permissions"])
            
            logger.info(f"WebSocket authenticated for user {user_id}")
            return user_info
            
        except Exception as e:
            logger.error(f"WebSocket authentication failed: {e}")
            return None
    
    def get_user_info(self, websocket: WebSocket) -> Optional[Dict]:
        """Get authenticated user info for a WebSocket connection."""
        return self.authenticated_connections.get(websocket)
    
    def is_authenticated(self, websocket: WebSocket) -> bool:
        """Check if a WebSocket connection is authenticated."""
        return websocket in self.authenticated_connections
    
    def has_permission(self, websocket: WebSocket, permission: str) -> bool:
        """Check if an authenticated user has a specific permission."""
        user_info = self.get_user_info(websocket)
        if not user_info:
            return False
        
        return permission in user_info.get("permissions", [])
    
    def remove_connection(self, websocket: WebSocket):
        """Remove authentication info for a disconnected WebSocket."""
        if websocket in self.authenticated_connections:
            user_info = self.authenticated_connections[websocket]
            user_id = user_info["user_id"]
            
            del self.authenticated_connections[websocket]
            
            # Clean up user permissions if no more connections
            if user_id not in [info["user_id"] for info in self.authenticated_connections.values()]:
                if user_id in self.user_permissions:
                    del self.user_permissions[user_id]
            
            logger.info(f"WebSocket authentication removed for user {user_id}")
    
    def get_authenticated_users(self) -> Set[str]:
        """Get set of currently authenticated user IDs."""
        return {info["user_id"] for info in self.authenticated_connections.values()}
    
    def get_stats(self) -> Dict:
        """Get authentication statistics."""
        return {
            "authenticated_connections": len(self.authenticated_connections),
            "unique_users": len(self.get_authenticated_users()),
            "user_permissions_cached": len(self.user_permissions)
        }


class WebSocketSecurityManager:
    """
    Comprehensive WebSocket security manager.
    Combines rate limiting, authentication, and security monitoring.
    """
    
    def __init__(self):
        self.rate_limiter = WebSocketRateLimiter()
        self.authenticator = WebSocketAuthenticator()
        self.security_events: deque = deque(maxlen=1000)  # Keep last 1000 events
    
    async def validate_connection(
        self,
        websocket: WebSocket,
        token: str,
        client_ip: str,
        required_permissions: Set[str] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Comprehensive connection validation.
        Returns (success, message, user_info).
        """
        try:
            # First authenticate the user
            user_info = await self.authenticator.authenticate_connection(
                websocket, token, required_permissions
            )
            
            if not user_info:
                self._log_security_event("authentication_failed", {
                    "client_ip": client_ip,
                    "token_provided": bool(token)
                })
                return False, "Authentication failed", None
            
            user_id = user_info["user_id"]
            
            # Check rate limits
            can_connect, rate_message = self.rate_limiter.can_connect(user_id, client_ip)
            if not can_connect:
                self._log_security_event("rate_limit_exceeded", {
                    "user_id": user_id,
                    "client_ip": client_ip,
                    "reason": rate_message
                })
                return False, rate_message, None
            
            # Register the connection
            self.rate_limiter.add_connection(user_id, client_ip)
            
            self._log_security_event("connection_established", {
                "user_id": user_id,
                "client_ip": client_ip
            })
            
            return True, "Connection validated", user_info
            
        except Exception as e:
            logger.error(f"Connection validation error: {e}")
            self._log_security_event("validation_error", {
                "client_ip": client_ip,
                "error": str(e)
            })
            return False, "Validation failed", None
    
    async def validate_message(
        self,
        websocket: WebSocket,
        client_ip: str,
        message_data: Dict
    ) -> Tuple[bool, str]:
        """
        Validate an incoming WebSocket message.
        Returns (allowed, message).
        """
        user_info = self.authenticator.get_user_info(websocket)
        if not user_info:
            return False, "Not authenticated"
        
        user_id = user_info["user_id"]
        
        # Check message rate limits
        can_send, rate_message = self.rate_limiter.can_send_message(user_id, client_ip)
        if not can_send:
            self._log_security_event("message_rate_limited", {
                "user_id": user_id,
                "client_ip": client_ip,
                "reason": rate_message
            })
            return False, rate_message
        
        # Record the message
        self.rate_limiter.record_message(user_id, client_ip)
        
        # Additional message validation can be added here
        # (e.g., content filtering, size limits, etc.)
        
        return True, "Message allowed"
    
    def cleanup_connection(self, websocket: WebSocket, client_ip: str):
        """Clean up security tracking for a disconnected WebSocket."""
        user_info = self.authenticator.get_user_info(websocket)
        
        if user_info:
            user_id = user_info["user_id"]
            self.rate_limiter.remove_connection(user_id, client_ip)
            
            self._log_security_event("connection_closed", {
                "user_id": user_id,
                "client_ip": client_ip
            })
        
        self.authenticator.remove_connection(websocket)
    
    def _log_security_event(self, event_type: str, event_data: Dict):
        """Log a security event."""
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": event_data
        }
        
        self.security_events.append(event)
        logger.info(f"Security event: {event_type} - {event_data}")
    
    def get_security_stats(self) -> Dict:
        """Get comprehensive security statistics."""
        return {
            "rate_limiter": self.rate_limiter.get_stats(),
            "authenticator": self.authenticator.get_stats(),
            "recent_events": len(self.security_events),
            "security_events_sample": list(self.security_events)[-10:]  # Last 10 events
        }
    
    def get_recent_security_events(self, limit: int = 50) -> List[Dict]:
        """Get recent security events."""
        return list(self.security_events)[-limit:]


# Global security manager instance
security_manager = WebSocketSecurityManager()


# Utility functions

def get_client_ip(websocket: WebSocket) -> str:
    """Extract client IP from WebSocket connection."""
    # Try to get real IP from headers (if behind proxy)
    forwarded_for = websocket.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = websocket.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection IP
    return websocket.client.host if websocket.client else "unknown"


async def secure_websocket_connection(
    websocket: WebSocket,
    token: str,
    required_permissions: Set[str] = None
) -> Tuple[bool, str, Optional[Dict]]:
    """
    Secure WebSocket connection with authentication and rate limiting.
    Returns (success, message, user_info).
    """
    client_ip = get_client_ip(websocket)
    
    return await security_manager.validate_connection(
        websocket, token, client_ip, required_permissions
    )


async def validate_websocket_message(
    websocket: WebSocket,
    message_data: Dict
) -> tuple[bool, str]:
    """
    Validate a WebSocket message for security and rate limiting.
    Returns (allowed, message).
    """
    client_ip = get_client_ip(websocket)
    
    return await security_manager.validate_message(
        websocket, client_ip, message_data
    )


def cleanup_websocket_security(websocket: WebSocket):
    """Clean up security tracking for a WebSocket connection."""
    client_ip = get_client_ip(websocket)
    security_manager.cleanup_connection(websocket, client_ip)