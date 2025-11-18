"""User-related database models"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    session_id = Column(String, unique=True, index=True, nullable=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    itineraries = relationship("Itinerary", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.username}')>"


class UserProfile(Base):
    """User profile model with preferences and resume info."""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    major = Column(String, nullable=True)
    skills = Column(Text, nullable=True)  # JSON string of skills
    experience_level = Column(String, nullable=True)  # e.g., "Entry-Level", "Experienced"
    resume_path = Column(String, nullable=True)  # Path to uploaded resume
    target_roles = Column(Text, nullable=True)  # JSON string of target roles
    time_budget_minutes = Column(Integer, default=180)  # 3 hours default

    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(major='{self.major}')>"
