"""
Company-related API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.company import Company, PositionType, MajorRecruited

router = APIRouter()


@router.get("/")
async def get_companies(
    db: Session = Depends(get_db),
    major: Optional[str] = Query(None, description="Filter by major"),
    position_type: Optional[str] = Query(None, description="Filter by position type"),
    ballroom: Optional[str] = Query(None, description="Filter by ballroom"),
    search: Optional[str] = Query(None, description="Search company name"),
    platinum_only: bool = Query(False, description="Show only platinum sponsors"),
):
    """
    Get all companies with optional filters.

    - **major**: Filter companies recruiting for specific major
    - **position_type**: Filter by position type (Entry-Level, Internship, Co-Op)
    - **ballroom**: Filter by ballroom location
    - **search**: Search company names
    - **platinum_only**: Show only platinum sponsors
    """
    query = db.query(Company)

    # Apply filters
    if platinum_only:
        query = query.filter(Company.is_platinum_sponsor == True)

    if ballroom:
        query = query.filter(Company.ballroom == ballroom)

    if search:
        query = query.filter(Company.name.ilike(f"%{search}%"))

    companies = query.all()

    # Filter by major (requires join)
    if major:
        companies = [
            c for c in companies
            if any(m.major_name == major for m in c.majors_recruited)
        ]

    # Filter by position type (requires join)
    if position_type:
        companies = [
            c for c in companies
            if any(p.position_type.startswith(position_type) for p in c.position_types)
        ]

    # Format response
    result = []
    for company in companies:
        result.append({
            "id": company.id,
            "name": company.name,
            "booth_number": company.booth_number,
            "ballroom": company.ballroom,
            "is_platinum_sponsor": company.is_platinum_sponsor,
            "position_types": [p.position_type for p in company.position_types],
            "majors": [m.major_name for m in company.majors_recruited],
            "website": company.website,
            "careers_url": company.careers_url,
        })

    return {"companies": result, "total": len(result)}


@router.get("/{company_id}")
async def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get company details by ID."""
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return {
        "id": company.id,
        "name": company.name,
        "booth_number": company.booth_number,
        "ballroom": company.ballroom,
        "is_platinum_sponsor": company.is_platinum_sponsor,
        "position_types": [p.position_type for p in company.position_types],
        "majors": [m.major_name for m in company.majors_recruited],
        "website": company.website,
        "careers_url": company.careers_url,
        "description": company.description,
        "sector": company.sector,
    }


@router.get("/booth/{booth_number}")
async def get_company_by_booth(booth_number: str, db: Session = Depends(get_db)):
    """Get company by booth number."""
    company = db.query(Company).filter(Company.booth_number == booth_number).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found at this booth")

    return {
        "id": company.id,
        "name": company.name,
        "booth_number": company.booth_number,
        "ballroom": company.ballroom,
        "is_platinum_sponsor": company.is_platinum_sponsor,
        "position_types": [p.position_type for p in company.position_types],
        "majors": [m.major_name for m in company.majors_recruited],
    }


@router.get("/filters/majors")
async def get_majors(db: Session = Depends(get_db)):
    """Get all unique majors recruited."""
    majors = db.query(MajorRecruited.major_name).distinct().all()
    return {"majors": sorted([m[0] for m in majors])}


@router.get("/filters/ballrooms")
async def get_ballrooms(db: Session = Depends(get_db)):
    """Get all unique ballroom locations."""
    ballrooms = db.query(Company.ballroom).distinct().all()
    return {"ballrooms": sorted([b[0] for b in ballrooms])}


@router.get("/filters/position-types")
async def get_position_types(db: Session = Depends(get_db)):
    """Get all unique position types."""
    position_types = db.query(PositionType.position_type).distinct().all()
    # Extract base types (Entry-Level, Internship, Co-Op)
    base_types = set()
    for pt in position_types:
        if "Entry-Level" in pt[0] or "Full-Time" in pt[0]:
            base_types.add("Entry-Level/Full-Time")
        if "Internship" in pt[0]:
            base_types.add("Internships")
        if "Co-Op" in pt[0]:
            base_types.add("Co-Op")

    return {"position_types": sorted(list(base_types))}
