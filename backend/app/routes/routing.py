"""
Routing and optimization API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from ..database import get_db
from ..models.company import Company
from ..models.booth import Booth
from ..models.user import User
from ..models.itinerary import Itinerary, ItineraryItem
from ..services.graph_builder import GraphBuilder
from ..services.routing_optimizer import RoutingOptimizer
from ..config import get_settings

settings = get_settings()
router = APIRouter()


class RouteRequest(BaseModel):
    company_ids: List[int]
    user_id: Optional[int] = None
    time_budget_minutes: int = 180
    start_location: str = "entrance"


class CompanyScore(BaseModel):
    company_id: int
    score: float


@router.post("/optimize")
async def optimize_route(request: RouteRequest, db: Session = Depends(get_db)):
    """
    Generate optimized visiting route for selected companies.

    Uses greedy heuristic to maximize company value within time budget.
    """
    if not request.company_ids:
        raise HTTPException(status_code=400, detail="No companies provided")

    # Get companies
    companies = db.query(Company).filter(Company.id.in_(request.company_ids)).all()

    if not companies:
        raise HTTPException(status_code=404, detail="No companies found")

    # Get booths for graph building
    booths = db.query(Booth).all()
    booth_data = [
        {
            "booth_number": b.booth_number,
            "coordinate_x": b.coordinate_x or 0,
            "coordinate_y": b.coordinate_y or 0,
            "ballroom": b.ballroom,
        }
        for b in booths
    ]

    # Build graph
    graph_builder = GraphBuilder(avg_walking_speed_mps=settings.avg_walking_speed_mps)

    if booth_data:
        graph_builder.build_from_booths(booth_data)
    else:
        # No booth coordinates, use default fallback
        pass

    # Prepare company data with scores (default to 1.0 for now)
    company_data = [
        {
            "id": c.id,
            "name": c.name,
            "booth_number": c.booth_number,
            "score": 1.0,  # Default score, will be replaced by scoring service
        }
        for c in companies
    ]

    # Optimize route
    optimizer = RoutingOptimizer(graph_builder)
    result = optimizer.greedy_route(
        companies=company_data,
        time_budget_minutes=request.time_budget_minutes,
        start_location=request.start_location,
        avg_interaction_time=settings.avg_interaction_time_min,
    )

    # Add company details to route
    company_map = {c.id: c for c in companies}
    for item in result["route"]:
        company = company_map[item["company_id"]]
        item["company_name"] = company.name
        item["ballroom"] = company.ballroom

    return result


@router.post("/calculate-time")
async def calculate_route_time(
    booth_sequence: List[str],
    avg_interaction_time: float = 5.0,
    db: Session = Depends(get_db),
):
    """Calculate total time for a given booth visiting sequence."""
    # Get booths for graph
    booths = db.query(Booth).all()
    booth_data = [
        {
            "booth_number": b.booth_number,
            "coordinate_x": b.coordinate_x or 0,
            "coordinate_y": b.coordinate_y or 0,
            "ballroom": b.ballroom,
        }
        for b in booths
    ]

    # Build graph
    graph_builder = GraphBuilder()
    if booth_data:
        graph_builder.build_from_booths(booth_data)

    # Calculate time
    optimizer = RoutingOptimizer(graph_builder)
    total_time = optimizer.calculate_route_time(
        booth_sequence=booth_sequence,
        avg_interaction_time=avg_interaction_time,
    )

    return {
        "booth_sequence": booth_sequence,
        "total_time_minutes": total_time,
        "num_booths": len(booth_sequence),
    }


@router.get("/shortest-path")
async def shortest_path(
    start: str,
    end: str,
    db: Session = Depends(get_db),
):
    """Find shortest path between two booths."""
    # Build graph
    booths = db.query(Booth).all()
    booth_data = [
        {
            "booth_number": b.booth_number,
            "coordinate_x": b.coordinate_x or 0,
            "coordinate_y": b.coordinate_y or 0,
            "ballroom": b.ballroom,
        }
        for b in booths
    ]

    graph_builder = GraphBuilder()
    if booth_data:
        graph_builder.build_from_booths(booth_data)

    # Find path
    path, travel_time = graph_builder.dijkstra_path(start, end)

    if not path:
        raise HTTPException(
            status_code=404,
            detail=f"No path found from {start} to {end}"
        )

    return {
        "start": start,
        "end": end,
        "path": path,
        "travel_time_minutes": travel_time,
        "num_hops": len(path) - 1,
    }
