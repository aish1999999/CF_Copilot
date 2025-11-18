"""
Routing optimization service using greedy heuristic.

Solves the time-constrained orienteering problem to maximize company utility
while staying within the user's time budget.
"""
from typing import List, Dict, Tuple
from .graph_builder import GraphBuilder


class RoutingOptimizer:
    """Optimize booth visiting route for maximum value within time budget."""

    def __init__(self, graph_builder: GraphBuilder):
        """
        Initialize routing optimizer.

        Args:
            graph_builder: GraphBuilder instance with booth graph
        """
        self.graph = graph_builder

    def greedy_route(
        self,
        companies: List[Dict],
        time_budget_minutes: float,
        start_location: str = "entrance",
        avg_interaction_time: float = 5.0
    ) -> Dict:
        """
        Generate optimized route using greedy heuristic.

        Selects next booth with best marginal utility/time ratio.

        Args:
            companies: List of company dicts with keys: id, booth_number, score
            time_budget_minutes: Total time budget in minutes
            start_location: Starting location (booth number or "entrance")
            avg_interaction_time: Average time at each booth in minutes

        Returns:
            Dictionary with route, total_time, total_score, and companies
        """
        if not companies:
            return {
                "route": [],
                "total_time": 0,
                "total_score": 0,
                "companies": [],
                "message": "No companies provided"
            }

        # Initialize
        current_location = start_location
        time_remaining = time_budget_minutes
        route = []
        visited = set()
        total_score = 0
        total_time = 0
        unvisited = [(c["id"], c["booth_number"], c.get("score", 1.0)) for c in companies]

        # Greedy selection loop
        while unvisited and time_remaining > 0:
            best_company = None
            best_ratio = -1
            best_travel_time = 0

            # Find company with best utility/time ratio
            for company_id, booth_number, score in unvisited:
                # Calculate travel time
                if current_location == start_location:
                    travel_time = 2.0  # Assume 2 min from entrance
                else:
                    try:
                        _, travel_time = self.graph.dijkstra_path(current_location, booth_number)
                    except:
                        travel_time = 3.0  # Default fallback

                # Total time for this visit
                visit_time = travel_time + avg_interaction_time

                # Check if we have enough time
                if visit_time > time_remaining:
                    continue

                # Calculate utility ratio
                ratio = score / visit_time

                if ratio > best_ratio:
                    best_ratio = ratio
                    best_company = (company_id, booth_number, score)
                    best_travel_time = travel_time

            # No more companies can be visited within time budget
            if best_company is None:
                break

            # Add company to route
            company_id, booth_number, score = best_company
            route.append({
                "company_id": company_id,
                "booth_number": booth_number,
                "travel_time": best_travel_time,
                "service_time": avg_interaction_time,
                "arrival_time": total_time + best_travel_time,
                "score": score,
            })

            # Update state
            visited.add(company_id)
            unvisited = [(cid, bn, s) for cid, bn, s in unvisited if cid != company_id]
            current_location = booth_number
            total_time += best_travel_time + avg_interaction_time
            time_remaining -= (best_travel_time + avg_interaction_time)
            total_score += score

        return {
            "route": route,
            "total_time": total_time,
            "total_score": total_score,
            "companies_visited": len(route),
            "time_remaining": time_budget_minutes - total_time,
        }

    def calculate_route_time(
        self,
        booth_sequence: List[str],
        avg_interaction_time: float = 5.0,
        start_location: str = "entrance"
    ) -> float:
        """
        Calculate total time for a given booth sequence.

        Args:
            booth_sequence: Ordered list of booth numbers
            avg_interaction_time: Time at each booth
            start_location: Starting location

        Returns:
            Total time in minutes
        """
        total_time = 0
        current = start_location

        for booth in booth_sequence:
            # Travel time
            if current == start_location:
                travel_time = 2.0
            else:
                try:
                    _, travel_time = self.graph.dijkstra_path(current, booth)
                except:
                    travel_time = 3.0

            total_time += travel_time + avg_interaction_time
            current = booth

        return total_time
