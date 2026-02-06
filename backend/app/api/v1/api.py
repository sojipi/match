"""
Main API router for version 1.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, matches, sessions, personality, avatar, notifications, ai_agents, scenarios, compatibility

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(personality.router, prefix="/personality", tags=["personality"])
api_router.include_router(avatar.router, prefix="/avatar", tags=["avatar"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(ai_agents.router, prefix="/ai-agents", tags=["ai-agents"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(compatibility.router, prefix="/compatibility", tags=["compatibility"])