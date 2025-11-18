"""Booth-related database models"""
from sqlalchemy import Column, Integer, String, Float
from ..database import Base


class Booth(Base):
    """Booth model representing physical location on the floor map."""

    __tablename__ = "booths"

    id = Column(Integer, primary_key=True, index=True)
    booth_number = Column(String, unique=True, index=True, nullable=False)
    ballroom = Column(String, nullable=False)
    coordinate_x = Column(Float, nullable=True)
    coordinate_y = Column(Float, nullable=True)
    queue_length = Column(Integer, default=0)  # Current queue length
    service_time_estimate = Column(Float, default=5.0)  # minutes

    def __repr__(self):
        return f"<Booth(number='{self.booth_number}', ballroom='{self.ballroom}')>"
