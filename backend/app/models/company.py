"""Company-related database models"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from ..database import Base


class Company(Base):
    """Company model representing a company at the career fair."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    booth_number = Column(String, nullable=False)
    ballroom = Column(String, nullable=False)
    is_platinum_sponsor = Column(Boolean, default=False)
    website = Column(String, nullable=True)
    careers_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    sector = Column(String, nullable=True)

    # Relationships
    position_types = relationship("PositionType", back_populates="company", cascade="all, delete-orphan")
    majors_recruited = relationship("MajorRecruited", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(name='{self.name}', booth='{self.booth_number}')>"


class PositionType(Base):
    """Position types offered by a company."""

    __tablename__ = "position_types"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    position_type = Column(String, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="position_types")

    def __repr__(self):
        return f"<PositionType(type='{self.position_type}')>"


class MajorRecruited(Base):
    """Majors recruited by a company."""

    __tablename__ = "majors_recruited"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    major_name = Column(String, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="majors_recruited")

    def __repr__(self):
        return f"<MajorRecruited(major='{self.major_name}')>"
