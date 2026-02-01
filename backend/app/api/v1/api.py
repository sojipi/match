"""
Main API router for version 1.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, matches, sessions

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])