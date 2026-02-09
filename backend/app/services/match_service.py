"""
Match discovery and management service.
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
from datetime import datetime, date
import math

from app.models.user import User, PersonalityProfile, DatingPreferences, UserPhoto
from app.models.match import Match, MatchStatus, InterestLevel
from app.core.database import get_db


class MatchService:
    """Service for match discovery and management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def discover_matches(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[dict] = None
    ) -> Tuple[List[dict], int]:
        """
        Discover potential matches for a user.
        
        Args:
            user_id: ID of the user looking for matches
            limit: Maximum number of matches to return
            offset: Number of matches to skip
            filters: Optional filters to apply
            
        Returns:
            Tuple of (matches list, total count)
        """
        # Get the current user's preferences and profile
        current_user_query = select(User).options(
            selectinload(User.dating_preferences),
            selectinload(User.personality_profile)
        ).where(User.id == user_id)
        
        result = await self.db.execute(current_user_query)
        current_user = result.scalar_one_or_none()
        
        if not current_user:
            return [], 0
        
        # Build the base query for potential matches
        query = select(User).options(
            selectinload(User.photos),
            selectinload(User.personality_profile),
            selectinload(User.dating_preferences)
        ).where(
            User.id != user_id  # Only exclude self
        )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar()
        
        # Apply pagination and execute
        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        potential_matches = result.scalars().all()
        
        # Convert to response format with compatibility scores
        matches = []
        for match_user in potential_matches:
            compatibility_score = await self._calculate_compatibility_preview(
                current_user, match_user
            )
            
            # Get primary photo
            primary_photo = None
            if match_user.photos:
                primary_photo = next(
                    (photo.file_url for photo in match_user.photos if photo.is_primary),
                    match_user.photos[0].file_url if match_user.photos else None
                )
            
            # Calculate age
            age = None
            if match_user.date_of_birth:
                today = date.today()
                age = today.year - match_user.date_of_birth.year
                if today.month < match_user.date_of_birth.month or \
                   (today.month == match_user.date_of_birth.month and today.day < match_user.date_of_birth.day):
                    age -= 1
            
            # Get shared interests (simplified for now)
            shared_interests = await self._get_shared_interests(current_user, match_user)
            
            matches.append({
                "user_id": str(match_user.id),
                "display_name": f"{match_user.first_name} {match_user.last_name[0]}.",
                "age": age,
                "location": match_user.location or "Location not specified",
                "primary_photo_url": primary_photo,
                "bio_preview": (match_user.bio[:100] + "...") if match_user.bio and len(match_user.bio) > 100 else (match_user.bio or "No bio available"),
                "compatibility_preview": round(compatibility_score, 2),
                "shared_interests": shared_interests,
                "personality_highlights": await self._get_personality_highlights(match_user),
                "is_online": self._is_user_online(match_user),
                "mutual_connections": 0  # TODO: Implement mutual connections
            })
        
        return matches, total_count
    
    async def like_user(self, user_id: str, target_user_id: str) -> dict:
        """
        Like a potential match.
        
        Args:
            user_id: ID of the user liking
            target_user_id: ID of the user being liked
            
        Returns:
            Dictionary with like result and mutual match status
        """
        # Import here to avoid circular imports
        from app.services.notification_service import NotificationService
        
        # Check if match already exists
        existing_match_query = select(Match).where(
            or_(
                and_(Match.user1_id == user_id, Match.user2_id == target_user_id),
                and_(Match.user1_id == target_user_id, Match.user2_id == user_id)
            )
        )
        
        result = await self.db.execute(existing_match_query)
        existing_match = result.scalar_one_or_none()
        
        notification_service = NotificationService(self.db)
        
        if existing_match:
            # Update existing match
            if existing_match.user1_id == user_id:
                existing_match.user1_interest = InterestLevel.LIKE
            else:
                existing_match.user2_interest = InterestLevel.LIKE
            
            # Check for mutual match
            is_mutual = (existing_match.user1_interest == InterestLevel.LIKE and 
                        existing_match.user2_interest == InterestLevel.LIKE)
            
            if is_mutual:
                existing_match.status = MatchStatus.MUTUAL
                # Calculate compatibility score
                existing_match.compatibility_score = await self._calculate_full_compatibility(
                    existing_match.user1_id, existing_match.user2_id
                )
                
                # Send mutual match notifications
                await notification_service.notify_mutual_match(
                    user1_id=str(existing_match.user1_id),
                    user2_id=str(existing_match.user2_id),
                    match_id=str(existing_match.id)
                )
            else:
                # Send like notification to the target user
                await notification_service.notify_like_received(
                    user_id=target_user_id,
                    liker_user_id=user_id
                )
            
            existing_match.updated_at = datetime.utcnow()
            match_id = str(existing_match.id)
            
        else:
            # Create new match
            new_match = Match(
                user1_id=user_id,
                user2_id=target_user_id,
                user1_interest=InterestLevel.LIKE,
                status=MatchStatus.PENDING
            )
            self.db.add(new_match)
            await self.db.flush()  # Get the ID
            
            # Send like notification to the target user
            await notification_service.notify_like_received(
                user_id=target_user_id,
                liker_user_id=user_id
            )
            
            is_mutual = False
            match_id = str(new_match.id)
        
        await self.db.commit()
        
        return {
            "message": f"Liked user {target_user_id}",
            "is_mutual": is_mutual,
            "match_id": match_id
        }
    
    async def pass_user(self, user_id: str, target_user_id: str) -> dict:
        """
        Pass on a potential match.
        
        Args:
            user_id: ID of the user passing
            target_user_id: ID of the user being passed
            
        Returns:
            Dictionary with pass result
        """
        # Check if match already exists
        existing_match_query = select(Match).where(
            or_(
                and_(Match.user1_id == user_id, Match.user2_id == target_user_id),
                and_(Match.user1_id == target_user_id, Match.user2_id == user_id)
            )
        )
        
        result = await self.db.execute(existing_match_query)
        existing_match = result.scalar_one_or_none()
        
        if existing_match:
            # Update existing match
            if existing_match.user1_id == user_id:
                existing_match.user1_interest = InterestLevel.PASS
            else:
                existing_match.user2_interest = InterestLevel.PASS
            
            existing_match.updated_at = datetime.utcnow()
            
        else:
            # Create new match with pass
            new_match = Match(
                user1_id=user_id,
                user2_id=target_user_id,
                user1_interest=InterestLevel.PASS,
                status=MatchStatus.PENDING
            )
            self.db.add(new_match)
        
        await self.db.commit()
        
        return {"message": f"Passed on user {target_user_id}"}
    
    async def get_match_history(self, user_id: str) -> List[dict]:
        """
        Get user's match history.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of match history items
        """
        query = select(Match).options(
            selectinload(Match.user1).selectinload(User.photos),
            selectinload(Match.user2).selectinload(User.photos)
        ).where(
            and_(
                or_(Match.user1_id == user_id, Match.user2_id == user_id),
                Match.status == MatchStatus.MUTUAL
            )
        ).order_by(Match.created_at.desc())
        
        result = await self.db.execute(query)
        matches = result.scalars().all()
        
        history = []
        for match in matches:
            # Determine the other user
            other_user = match.user2 if match.user1_id == user_id else match.user1
            
            # Get primary photo
            primary_photo = None
            if other_user.photos:
                primary_photo = next(
                    (photo.file_url for photo in other_user.photos if photo.is_primary),
                    other_user.photos[0].file_url if other_user.photos else None
                )
            
            history.append({
                "id": str(match.id),
                "user": {
                    "id": str(other_user.id),
                    "name": f"{other_user.first_name} {other_user.last_name[0]}.",
                    "photo_url": primary_photo
                },
                "compatibility_score": match.compatibility_score or 0.0,
                "status": match.status.value,
                "conversation_count": match.conversation_count,
                "last_interaction": match.last_interaction.isoformat() if match.last_interaction else None,
                "created_at": match.created_at.isoformat()
            })
        
        return history
    
    async def _calculate_compatibility_preview(self, user1: User, user2: User) -> float:
        """Calculate a quick compatibility preview score."""
        if not user1.personality_profile or not user2.personality_profile:
            return 0.5  # Default neutral score
        
        p1 = user1.personality_profile
        p2 = user2.personality_profile
        
        # Simple compatibility calculation based on personality traits
        # This is a simplified version - in production, use more sophisticated algorithms
        trait_scores = []
        
        if p1.openness is not None and p2.openness is not None:
            trait_scores.append(1 - abs(p1.openness - p2.openness))
        
        if p1.conscientiousness is not None and p2.conscientiousness is not None:
            trait_scores.append(1 - abs(p1.conscientiousness - p2.conscientiousness))
        
        if p1.extraversion is not None and p2.extraversion is not None:
            # For extraversion, some difference can be good (complementary)
            diff = abs(p1.extraversion - p2.extraversion)
            trait_scores.append(1 - (diff * 0.7))  # Reduce penalty for differences
        
        if p1.agreeableness is not None and p2.agreeableness is not None:
            trait_scores.append(1 - abs(p1.agreeableness - p2.agreeableness))
        
        if p1.neuroticism is not None and p2.neuroticism is not None:
            # Lower neuroticism difference is better
            trait_scores.append(1 - abs(p1.neuroticism - p2.neuroticism))
        
        if trait_scores:
            return sum(trait_scores) / len(trait_scores)
        
        return 0.5
    
    async def _calculate_full_compatibility(self, user1_id: str, user2_id: str) -> float:
        """Calculate full compatibility score for mutual matches."""
        # This would implement a more comprehensive compatibility calculation
        # For now, return a placeholder
        return 0.85
    
    async def _get_shared_interests(self, user1: User, user2: User) -> List[str]:
        """Get shared interests between two users."""
        # This would analyze user profiles, preferences, and other data
        # For now, return placeholder interests
        return ["music", "travel", "fitness"]
    
    async def _get_personality_highlights(self, user: User) -> List[str]:
        """Get personality highlights for a user."""
        if not user.personality_profile:
            return []
        
        highlights = []
        p = user.personality_profile
        
        if p.extraversion and p.extraversion > 0.7:
            highlights.append("Outgoing")
        elif p.extraversion and p.extraversion < 0.3:
            highlights.append("Thoughtful")
        
        if p.openness and p.openness > 0.7:
            highlights.append("Creative")
        
        if p.conscientiousness and p.conscientiousness > 0.7:
            highlights.append("Organized")
        
        if p.agreeableness and p.agreeableness > 0.7:
            highlights.append("Compassionate")
        
        return highlights[:3]  # Return top 3 highlights
    
    def _is_user_online(self, user: User) -> bool:
        """Check if user is currently online."""
        if not user.last_active:
            return False

        # Consider user online if active within last 15 minutes
        # Make datetime timezone-aware if needed
        from datetime import timezone
        now = datetime.now(timezone.utc)
        last_active = user.last_active

        # If last_active is naive, make it aware
        if last_active.tzinfo is None:
            last_active = last_active.replace(tzinfo=timezone.utc)

        time_diff = now - last_active
        return time_diff.total_seconds() < 900  # 15 minutes
    
    async def get_match_by_id(self, match_id: str, user_id: str) -> dict:
        """
        Get match details by ID.
        
        Args:
            match_id: ID of the match
            user_id: ID of the requesting user (for verification)
            
        Returns:
            Dictionary with match details including both users' information
        """
        # Get the match with user details
        query = select(Match).options(
            selectinload(Match.user1).selectinload(User.photos),
            selectinload(Match.user2).selectinload(User.photos)
        ).where(Match.id == match_id)
        
        result = await self.db.execute(query)
        match = result.scalar_one_or_none()
        
        if not match:
            return None
        
        # Verify the requesting user is part of this match
        if str(match.user1_id) != user_id and str(match.user2_id) != user_id:
            return None
        
        # Get primary photos for both users
        user1_photo = None
        if match.user1.photos:
            user1_photo = next(
                (photo.file_url for photo in match.user1.photos if photo.is_primary),
                match.user1.photos[0].file_url if match.user1.photos else None
            )
        
        user2_photo = None
        if match.user2.photos:
            user2_photo = next(
                (photo.file_url for photo in match.user2.photos if photo.is_primary),
                match.user2.photos[0].file_url if match.user2.photos else None
            )
        
        return {
            "id": str(match.id),
            "user1_id": str(match.user1_id),
            "user2_id": str(match.user2_id),
            "user1_name": f"{match.user1.first_name} {match.user1.last_name[0]}.",
            "user2_name": f"{match.user2.first_name} {match.user2.last_name[0]}.",
            "user1_photo": user1_photo,
            "user2_photo": user2_photo,
            "status": match.status.value,
            "compatibility_score": match.compatibility_score,
            "created_at": match.created_at.isoformat()
        }