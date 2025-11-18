"""
Booth-related API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.booth import Booth

router = APIRouter()


@router.get("/")
async def get_booths(
    db: Session = Depends(get_db),
    ballroom: Optional[str] = None,
):
    """Get all booth locations."""
    query = db.query(Booth)

    if ballroom:
        query = query.filter(Booth.ballroom == ballroom)

    booths = query.all()

    return {
        "booths": [
            {
                "id": booth.id,
                "booth_number": booth.booth_number,
                "ballroom": booth.ballroom,
                "coordinates": {
                    "x": booth.coordinate_x,
                    "y": booth.coordinate_y,
                },
                "queue_length": booth.queue_length,
                "service_time_estimate": booth.service_time_estimate,
            }
            for booth in booths
        ],
        "total": len(booths),
    }


@router.get("/{booth_number}")
async def get_booth(booth_number: str, db: Session = Depends(get_db)):
    """Get booth details by number."""
    booth = db.query(Booth).filter(Booth.booth_number == booth_number).first()

    if not booth:
        raise HTTPException(status_code=404, detail="Booth not found")

    return {
        "id": booth.id,
        "booth_number": booth.booth_number,
        "ballroom": booth.ballroom,
        "coordinates": {
            "x": booth.coordinate_x,
            "y": booth.coordinate_y,
        },
        "queue_length": booth.queue_length,
        "service_time_estimate": booth.service_time_estimate,
    }


@router.patch("/{booth_number}/queue")
async def update_queue_length(
    booth_number: str,
    queue_length: int,
    db: Session = Depends(get_db),
):
    """Update queue length for a booth."""
    booth = db.query(Booth).filter(Booth.booth_number == booth_number).first()

    if not booth:
        raise HTTPException(status_code=404, detail="Booth not found")

    booth.queue_length = queue_length
    db.commit()
    db.refresh(booth)

    return {
        "booth_number": booth.booth_number,
        "queue_length": booth.queue_length,
        "message": "Queue length updated successfully",
    }
