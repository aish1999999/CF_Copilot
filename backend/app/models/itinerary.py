"""Itinerary-related database models"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Itinerary(Base):
    """Itinerary model representing a user's planned route."""

    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_time_estimate = Column(Float, nullable=True)  # in minutes
    total_score = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", back_populates="itineraries")
    items = relationship("ItineraryItem", back_populates="itinerary", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Itinerary(name='{self.name}', user_id={self.user_id})>"


class ItineraryItem(Base):
    """Individual item in an itinerary (booth visit)."""

    __tablename__ = "itinerary_items"

    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    sequence = Column(Integer, nullable=False)  # Order in the route
    estimated_arrival_time = Column(Float, nullable=True)  # minutes from start
    estimated_service_time = Column(Float, nullable=True)  # minutes
    estimated_travel_time = Column(Float, nullable=True)  # minutes from previous
    score = Column(Float, nullable=True)

    # Relationships
    itinerary = relationship("Itinerary", back_populates="items")

    def __repr__(self):
        return f"<ItineraryItem(sequence={self.sequence}, company_id={self.company_id})>"
