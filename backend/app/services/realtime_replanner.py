"""
Real-time route replanning service.

Handles dynamic replanning scenarios:
- Queue length changes
- Booth closures
- Time delays
- New company additions
- User preference changes
"""

import logging
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from .graph_builder import GraphBuilder
from .routing_optimizer import RoutingOptimizer

logger = logging.getLogger(__name__)


class RealtimeReplanner:
    """Service for real-time route adjustments."""

    def __init__(
        self,
        graph_builder: GraphBuilder,
        routing_optimizer: RoutingOptimizer
    ):
        """
        Initialize real-time replanner.

        Args:
            graph_builder: GraphBuilder instance
            routing_optimizer: RoutingOptimizer instance
        """
        self.graph = graph_builder
        self.optimizer = routing_optimizer
        self.logger = logger

    def replan_on_delay(
        self,
        current_route: List[Dict],
        current_position: int,
        delay_minutes: float,
        time_budget_minutes: float,
        companies: List[Dict],
        avg_interaction_time: float = 5.0
    ) -> Dict:
        """
        Replan route when a delay occurs.

        Args:
            current_route: Current planned route
            current_position: Index of current/next stop
            delay_minutes: Delay in minutes
            time_budget_minutes: Original time budget
            companies: All companies data
            avg_interaction_time: Avg time at booth

        Returns:
            Dict with new route and metadata
        """
        # Calculate time already spent
        time_spent = sum(
            stop["travel_time"] + stop["service_time"]
            for stop in current_route[:current_position]
        )

        # New time budget
        new_budget = time_budget_minutes - time_spent - delay_minutes

        if new_budget <= 0:
            return {
                "route": [],
                "message": "No time remaining after delay",
                "replanned": True,
                "delay_impact": "severe"
            }

        # Get remaining unvisited companies
        visited_ids = {stop["company_id"] for stop in current_route[:current_position]}
        remaining_companies = [
            c for c in companies
            if c["id"] not in visited_ids
        ]

        # Current location
        current_location = (
            current_route[current_position - 1]["booth_number"]
            if current_position > 0
            else "entrance"
        )

        # Reoptimize remaining route
        new_route = self.optimizer.greedy_route(
            remaining_companies,
            new_budget,
            start_location=current_location,
            avg_interaction_time=avg_interaction_time
        )

        # Determine impact level
        original_remaining = len(current_route) - current_position
        new_remaining = len(new_route["route"])

        if new_remaining < original_remaining * 0.5:
            impact = "severe"
        elif new_remaining < original_remaining * 0.8:
            impact = "moderate"
        else:
            impact = "minor"

        return {
            "route": new_route["route"],
            "total_time": new_route["total_time"],
            "total_score": new_route["total_score"],
            "companies_visited": new_remaining,
            "replanned": True,
            "delay_impact": impact,
            "companies_dropped": original_remaining - new_remaining,
            "message": f"Route replanned due to {delay_minutes} min delay"
        }

    def replan_on_queue_change(
        self,
        current_route: List[Dict],
        current_position: int,
        queue_updates: Dict[str, float],  # booth_number -> new_wait_time
        time_budget_minutes: float,
        companies: List[Dict],
        avg_interaction_time: float = 5.0
    ) -> Dict:
        """
        Replan route when queue lengths change.

        Args:
            current_route: Current route
            current_position: Current position
            queue_updates: Dict of booth_number -> new wait time
            time_budget_minutes: Time budget
            companies: All companies
            avg_interaction_time: Base interaction time

        Returns:
            Dict with updated route
        """
        # Update companies with new queue times
        updated_companies = []
        for company in companies:
            company_copy = company.copy()
            booth = company["booth_number"]

            if booth in queue_updates:
                # Add queue wait time to interaction time
                company_copy["queue_time"] = queue_updates[booth]

            updated_companies.append(company_copy)

        # Calculate time spent
        time_spent = sum(
            stop["travel_time"] + stop["service_time"]
            for stop in current_route[:current_position]
        )

        remaining_budget = time_budget_minutes - time_spent

        # Get unvisited companies
        visited_ids = {stop["company_id"] for stop in current_route[:current_position]}
        remaining_companies = [
            c for c in updated_companies
            if c["id"] not in visited_ids
        ]

        # Current location
        current_location = (
            current_route[current_position - 1]["booth_number"]
            if current_position > 0
            else "entrance"
        )

        # Reoptimize with updated queue times
        # Adjust interaction time based on queue
        new_route_data = []
        for company in remaining_companies:
            interaction_time = avg_interaction_time + company.get("queue_time", 0)

            # Rescale score based on queue time (penalize long queues)
            original_score = company.get("score", 1.0)
            queue_penalty = max(0.5, 1.0 - company.get("queue_time", 0) / 20.0)
            adjusted_score = original_score * queue_penalty

            new_route_data.append({
                **company,
                "score": adjusted_score,
                "effective_interaction_time": interaction_time
            })

        # Reoptimize
        new_route = self.optimizer.greedy_route(
            new_route_data,
            remaining_budget,
            start_location=current_location,
            avg_interaction_time=avg_interaction_time
        )

        return {
            **new_route,
            "replanned": True,
            "reason": "queue_change",
            "message": "Route updated based on current queue lengths"
        }

    def replan_on_booth_closure(
        self,
        current_route: List[Dict],
        current_position: int,
        closed_booths: Set[str],
        time_budget_minutes: float,
        companies: List[Dict],
        avg_interaction_time: float = 5.0
    ) -> Dict:
        """
        Replan route when booths close unexpectedly.

        Args:
            current_route: Current route
            current_position: Current position
            closed_booths: Set of closed booth numbers
            time_budget_minutes: Time budget
            companies: All companies
            avg_interaction_time: Avg interaction time

        Returns:
            Dict with updated route
        """
        # Remove closed booths from remaining route
        remaining_route = [
            stop for stop in current_route[current_position:]
            if stop["booth_number"] not in closed_booths
        ]

        # If no changes needed
        if len(remaining_route) == len(current_route[current_position:]):
            return {
                "route": remaining_route,
                "replanned": False,
                "message": "No changes needed - closed booths not in route"
            }

        # Calculate remaining budget
        time_spent = sum(
            stop["travel_time"] + stop["service_time"]
            for stop in current_route[:current_position]
        )
        remaining_budget = time_budget_minutes - time_spent

        # Get available companies (excluding closed)
        visited_ids = {stop["company_id"] for stop in current_route[:current_position]}
        available_companies = [
            c for c in companies
            if c["booth_number"] not in closed_booths
            and c["id"] not in visited_ids
        ]

        # Current location
        current_location = (
            current_route[current_position - 1]["booth_number"]
            if current_position > 0
            else "entrance"
        )

        # Reoptimize
        new_route = self.optimizer.greedy_route(
            available_companies,
            remaining_budget,
            start_location=current_location,
            avg_interaction_time=avg_interaction_time
        )

        closed_count = len([
            stop for stop in current_route[current_position:]
            if stop["booth_number"] in closed_booths
        ])

        return {
            **new_route,
            "replanned": True,
            "reason": "booth_closure",
            "booths_closed": list(closed_booths),
            "companies_affected": closed_count,
            "message": f"{closed_count} planned stops were closed and removed"
        }

    def add_priority_company(
        self,
        current_route: List[Dict],
        current_position: int,
        new_company: Dict,
        time_budget_minutes: float,
        companies: List[Dict],
        avg_interaction_time: float = 5.0,
        insert_asap: bool = True
    ) -> Dict:
        """
        Add a high-priority company to existing route.

        Args:
            current_route: Current route
            current_position: Current position
            new_company: New company to add
            time_budget_minutes: Time budget
            companies: All companies
            avg_interaction_time: Avg interaction time
            insert_asap: If True, insert as next stop; else reoptimize

        Returns:
            Dict with updated route
        """
        if insert_asap:
            # Insert as next stop
            current_location = (
                current_route[current_position - 1]["booth_number"]
                if current_position > 0
                else "entrance"
            )

            # Calculate travel time to new company
            try:
                _, travel_time = self.graph.dijkstra_path(
                    current_location,
                    new_company["booth_number"]
                )
            except:
                travel_time = 3.0

            # Create new stop
            cumulative_time = sum(
                stop["travel_time"] + stop["service_time"]
                for stop in current_route[:current_position]
            )

            new_stop = {
                "company_id": new_company["id"],
                "booth_number": new_company["booth_number"],
                "travel_time": travel_time,
                "service_time": avg_interaction_time,
                "arrival_time": cumulative_time + travel_time,
                "score": new_company.get("score", 1.0),
                "priority": True
            }

            # Insert into route
            updated_route = (
                current_route[:current_position] +
                [new_stop] +
                current_route[current_position:]
            )

            # Recalculate times for subsequent stops
            updated_route = self._recalculate_times(updated_route, current_position)

            # Check if still within budget
            total_time = sum(
                stop["travel_time"] + stop["service_time"]
                for stop in updated_route
            )

            if total_time > time_budget_minutes:
                # Need to drop some stops
                updated_route = self._trim_route_to_budget(
                    updated_route,
                    time_budget_minutes
                )

            return {
                "route": updated_route[current_position:],
                "replanned": True,
                "reason": "priority_addition",
                "message": f"Added {new_company['name']} as priority stop"
            }

        else:
            # Reoptimize with new company included
            visited_ids = {stop["company_id"] for stop in current_route[:current_position]}

            all_companies = [
                c for c in companies
                if c["id"] not in visited_ids
            ] + [new_company]

            time_spent = sum(
                stop["travel_time"] + stop["service_time"]
                for stop in current_route[:current_position]
            )

            current_location = (
                current_route[current_position - 1]["booth_number"]
                if current_position > 0
                else "entrance"
            )

            new_route = self.optimizer.greedy_route(
                all_companies,
                time_budget_minutes - time_spent,
                start_location=current_location,
                avg_interaction_time=avg_interaction_time
            )

            return {
                **new_route,
                "replanned": True,
                "reason": "priority_addition_optimized",
                "message": f"Route reoptimized with {new_company['name']}"
            }

    def _recalculate_times(
        self,
        route: List[Dict],
        from_position: int
    ) -> List[Dict]:
        """Recalculate arrival times from a position onwards."""
        updated_route = route[:from_position]

        cumulative_time = sum(
            stop["travel_time"] + stop["service_time"]
            for stop in route[:from_position]
        )

        current_location = (
            route[from_position - 1]["booth_number"]
            if from_position > 0
            else "entrance"
        )

        for stop in route[from_position:]:
            booth = stop["booth_number"]

            # Recalculate travel time
            try:
                _, travel_time = self.graph.dijkstra_path(current_location, booth)
            except:
                travel_time = stop["travel_time"]  # Fallback to original

            updated_stop = {
                **stop,
                "travel_time": travel_time,
                "arrival_time": cumulative_time + travel_time
            }

            updated_route.append(updated_stop)

            cumulative_time += travel_time + stop["service_time"]
            current_location = booth

        return updated_route

    def _trim_route_to_budget(
        self,
        route: List[Dict],
        budget: float
    ) -> List[Dict]:
        """Trim route to fit within time budget."""
        trimmed = []
        time_used = 0

        for stop in route:
            visit_time = stop["travel_time"] + stop["service_time"]

            if time_used + visit_time <= budget:
                trimmed.append(stop)
                time_used += visit_time
            else:
                break

        return trimmed

    def get_replan_recommendations(
        self,
        current_route: List[Dict],
        current_position: int,
        current_time_spent: float,
        time_budget_minutes: float
    ) -> Dict:
        """
        Analyze current progress and provide replan recommendations.

        Args:
            current_route: Current route
            current_position: Current position in route
            current_time_spent: Actual time spent so far
            time_budget_minutes: Original time budget

        Returns:
            Dict with recommendations
        """
        # Expected time at this position
        expected_time = sum(
            stop["travel_time"] + stop["service_time"]
            for stop in current_route[:current_position]
        )

        time_variance = current_time_spent - expected_time
        remaining_budget = time_budget_minutes - current_time_spent
        remaining_stops = len(current_route) - current_position

        recommendations = {
            "on_track": abs(time_variance) < 5.0,
            "time_variance": time_variance,
            "remaining_budget": remaining_budget,
            "remaining_stops": remaining_stops,
            "recommendations": []
        }

        # Running behind
        if time_variance > 5.0:
            recommendations["recommendations"].append({
                "type": "delay",
                "severity": "high" if time_variance > 15 else "medium",
                "message": f"Running {time_variance:.1f} min behind schedule",
                "action": "Consider skipping lower-priority stops"
            })

        # Running ahead
        if time_variance < -5.0:
            recommendations["recommendations"].append({
                "type": "ahead",
                "severity": "low",
                "message": f"Running {abs(time_variance):.1f} min ahead of schedule",
                "action": "Opportunity to add more companies"
            })

        # Tight remaining budget
        avg_stop_time = 8.0  # Estimated
        if remaining_budget < remaining_stops * avg_stop_time:
            recommendations["recommendations"].append({
                "type": "tight_budget",
                "severity": "high",
                "message": "Insufficient time for all remaining stops",
                "action": "Replan to drop lowest-priority companies"
            })

        return recommendations
