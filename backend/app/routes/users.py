"""
User-related API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from ..database import get_db
from ..models.user import User, UserProfile

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    email: str
    major: Optional[str] = None
    time_budget_minutes: int = 180


class ProfileUpdate(BaseModel):
    major: Optional[str] = None
    skills: Optional[str] = None
    experience_level: Optional[str] = None
    target_roles: Optional[str] = None
    time_budget_minutes: Optional[int] = None


@router.post("/")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user with profile."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create user
    session_id = str(uuid.uuid4())
    user = User(
        username=user_data.username,
        email=user_data.email,
        session_id=session_id,
    )
    db.add(user)
    db.flush()

    # Create profile
    profile = UserProfile(
        user_id=user.id,
        major=user_data.major,
        time_budget_minutes=user_data.time_budget_minutes,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "session_id": user.session_id,
        "message": "User created successfully",
    }


@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "session_id": user.session_id,
        "profile": {
            "major": user.profile.major if user.profile else None,
            "skills": user.profile.skills if user.profile else None,
            "experience_level": user.profile.experience_level if user.profile else None,
            "time_budget_minutes": user.profile.time_budget_minutes if user.profile else 180,
        } if user.profile else None,
    }


@router.patch("/{user_id}/profile")
async def update_profile(
    user_id: int,
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
):
    """Update user profile."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.profile:
        # Create profile if it doesn't exist
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.flush()
    else:
        profile = user.profile

    # Update profile fields
    if profile_data.major is not None:
        profile.major = profile_data.major
    if profile_data.skills is not None:
        profile.skills = profile_data.skills
    if profile_data.experience_level is not None:
        profile.experience_level = profile_data.experience_level
    if profile_data.target_roles is not None:
        profile.target_roles = profile_data.target_roles
    if profile_data.time_budget_minutes is not None:
        profile.time_budget_minutes = profile_data.time_budget_minutes

    db.commit()
    db.refresh(profile)

    return {
        "message": "Profile updated successfully",
        "profile": {
            "major": profile.major,
            "skills": profile.skills,
            "experience_level": profile.experience_level,
            "time_budget_minutes": profile.time_budget_minutes,
        },
    }
