"""
Advanced routing optimization using OR-Tools for ILP and metaheuristics.

Implements:
- Integer Linear Programming (ILP) for exact optimization
- Simulated Annealing for large-scale problems
- Genetic Algorithm for complex scenarios
"""

import logging
from typing import List, Dict, Tuple, Optional, Set
import random
from math import exp
from copy import deepcopy

try:
    from ortools.linear_solver import pywraplp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False

from .graph_builder import GraphBuilder

logger = logging.getLogger(__name__)


class AdvancedOptimizer:
    """Advanced optimization algorithms for route planning."""

    def __init__(self, graph_builder: GraphBuilder):
        """
        Initialize advanced optimizer.

        Args:
            graph_builder: GraphBuilder instance with booth graph
        """
        self.graph = graph_builder
        self.logger = logger

    def ilp_optimize(
        self,
        companies: List[Dict],
        time_budget_minutes: float,
        start_location: str = "entrance",
        avg_interaction_time: float = 5.0,
        solver_timeout_seconds: int = 30
    ) -> Dict:
        """
        Optimize route using Integer Linear Programming (ILP).

        Formulates as Orienteering Problem and solves using OR-Tools.

        Args:
            companies: List of company dicts with id, booth_number, score
            time_budget_minutes: Total time budget
            start_location: Starting location
            avg_interaction_time: Average time at each booth
            solver_timeout_seconds: Solver timeout

        Returns:
            Dict with optimized route and metadata
        """
        if not ORTOOLS_AVAILABLE:
            self.logger.error("OR-Tools not installed. Cannot use ILP optimization.")
            return {
                "route": [],
                "total_time": 0,
                "total_score": 0,
                "companies_visited": 0,
                "error": "OR-Tools not available"
            }

        if not companies:
            return {
                "route": [],
                "total_time": 0,
                "total_score": 0,
                "companies_visited": 0,
                "message": "No companies provided"
            }

        # Create solver
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            self.logger.error("SCIP solver not available")
            return {"error": "Solver not available"}

        solver.SetTimeLimit(solver_timeout_seconds * 1000)

        # Prepare data
        n = len(companies)
        booths = [c["booth_number"] for c in companies]
        scores = {c["booth_number"]: c.get("score", 1.0) for c in companies}

        # Calculate travel times between all pairs
        travel_times = {}
        for i, booth1 in enumerate(booths):
            for j, booth2 in enumerate(booths):
                if i != j:
                    try:
                        _, time = self.graph.dijkstra_path(booth1, booth2)
                        travel_times[(booth1, booth2)] = time
                    except:
                        travel_times[(booth1, booth2)] = 5.0

        # Decision variables
        # x[i] = 1 if booth i is visited
        x = {}
        for booth in booths:
            x[booth] = solver.BoolVar(f'x_{booth}')

        # u[i] = position in route (for subtour elimination)
        u = {}
        for i, booth in enumerate(booths):
            u[booth] = solver.IntVar(1, n, f'u_{booth}')

        # Objective: Maximize total score
        objective = solver.Objective()
        for booth in booths:
            objective.SetCoefficient(x[booth], scores[booth])
        objective.SetMaximization()

        # Constraint 1: Time budget
        time_expr = solver.Sum([
            x[booth] * avg_interaction_time for booth in booths
        ])

        # Add travel times (simplified - use average)
        avg_travel = sum(travel_times.values()) / len(travel_times) if travel_times else 2.0
        for booth in booths:
            time_expr += x[booth] * avg_travel

        solver.Add(time_expr <= time_budget_minutes)

        # Constraint 2: Subtour elimination (MTZ formulation)
        for i, booth1 in enumerate(booths):
            for j, booth2 in enumerate(booths):
                if i != j:
                    solver.Add(
                        u[booth1] - u[booth2] + n * (1 - x[booth1]) >= 1 - n
                    )

        # Solve
        status = solver.Solve()

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            # Extract solution
            selected_booths = [
                booth for booth in booths if x[booth].solution_value() > 0.5
            ]

            # Build route in order
            route = self._build_ordered_route(
                selected_booths,
                companies,
                start_location,
                avg_interaction_time
            )

            total_score = sum(scores[booth] for booth in selected_booths)
            total_time = sum(step["travel_time"] + step["service_time"] for step in route)

            return {
                "route": route,
                "total_time": total_time,
                "total_score": total_score,
                "companies_visited": len(selected_booths),
                "time_remaining": time_budget_minutes - total_time,
                "optimization_status": "optimal" if status == pywraplp.Solver.OPTIMAL else "feasible",
                "solve_time": solver.WallTime() / 1000.0
            }

        else:
            self.logger.warning(f"ILP solver failed with status: {status}")
            return {
                "route": [],
                "total_time": 0,
                "total_score": 0,
                "companies_visited": 0,
                "error": "No solution found"
            }

    def simulated_annealing(
        self,
        companies: List[Dict],
        time_budget_minutes: float,
        start_location: str = "entrance",
        avg_interaction_time: float = 5.0,
        initial_temp: float = 100.0,
        cooling_rate: float = 0.95,
        max_iterations: int = 1000
    ) -> Dict:
        """
        Optimize route using Simulated Annealing metaheuristic.

        Args:
            companies: List of company dicts
            time_budget_minutes: Time budget
            start_location: Starting location
            avg_interaction_time: Avg time at booth
            initial_temp: Initial temperature
            cooling_rate: Temperature cooling rate
            max_iterations: Maximum iterations

        Returns:
            Dict with optimized route
        """
        if not companies:
            return {
                "route": [],
                "total_time": 0,
                "total_score": 0,
                "companies_visited": 0
            }

        # Start with random feasible solution
        current_solution = self._generate_random_solution(
            companies,
            time_budget_minutes,
            avg_interaction_time
        )

        current_score = self._calculate_solution_score(current_solution)
        best_solution = deepcopy(current_solution)
        best_score = current_score

        temperature = initial_temp

        for iteration in range(max_iterations):
            # Generate neighbor solution
            neighbor = self._generate_neighbor(
                current_solution,
                companies,
                time_budget_minutes,
                avg_interaction_time
            )

            neighbor_score = self._calculate_solution_score(neighbor)

            # Accept or reject
            delta = neighbor_score - current_score

            if delta > 0 or random.random() < exp(delta / temperature):
                current_solution = neighbor
                current_score = neighbor_score

                if current_score > best_score:
                    best_solution = deepcopy(current_solution)
                    best_score = current_score

            # Cool down
            temperature *= cooling_rate

            if temperature < 0.1:
                break

        # Build final route
        route = self._build_ordered_route(
            best_solution,
            companies,
            start_location,
            avg_interaction_time
        )

        total_time = sum(step["travel_time"] + step["service_time"] for step in route)

        return {
            "route": route,
            "total_time": total_time,
            "total_score": best_score,
            "companies_visited": len(best_solution),
            "time_remaining": time_budget_minutes - total_time,
            "iterations": iteration + 1
        }

    def genetic_algorithm(
        self,
        companies: List[Dict],
        time_budget_minutes: float,
        start_location: str = "entrance",
        avg_interaction_time: float = 5.0,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1
    ) -> Dict:
        """
        Optimize route using Genetic Algorithm.

        Args:
            companies: List of company dicts
            time_budget_minutes: Time budget
            start_location: Starting location
            avg_interaction_time: Avg time at booth
            population_size: Size of population
            generations: Number of generations
            mutation_rate: Probability of mutation

        Returns:
            Dict with optimized route
        """
        if not companies:
            return {
                "route": [],
                "total_time": 0,
                "total_score": 0,
                "companies_visited": 0
            }

        # Initialize population
        population = [
            self._generate_random_solution(companies, time_budget_minutes, avg_interaction_time)
            for _ in range(population_size)
        ]

        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = [
                self._calculate_solution_score(individual)
                for individual in population
            ]

            # Selection (tournament selection)
            new_population = []
            for _ in range(population_size):
                parent1 = self._tournament_select(population, fitness_scores)
                parent2 = self._tournament_select(population, fitness_scores)

                # Crossover
                child = self._crossover(parent1, parent2)

                # Mutation
                if random.random() < mutation_rate:
                    child = self._mutate(
                        child,
                        companies,
                        time_budget_minutes,
                        avg_interaction_time
                    )

                new_population.append(child)

            population = new_population

        # Select best solution
        final_scores = [self._calculate_solution_score(ind) for ind in population]
        best_idx = final_scores.index(max(final_scores))
        best_solution = population[best_idx]

        # Build route
        route = self._build_ordered_route(
            best_solution,
            companies,
            start_location,
            avg_interaction_time
        )

        total_time = sum(step["travel_time"] + step["service_time"] for step in route)

        return {
            "route": route,
            "total_time": total_time,
            "total_score": max(final_scores),
            "companies_visited": len(best_solution),
            "time_remaining": time_budget_minutes - total_time,
            "generations": generations
        }

    def _generate_random_solution(
        self,
        companies: List[Dict],
        time_budget: float,
        avg_interaction_time: float
    ) -> List[str]:
        """Generate random feasible solution (booth numbers)."""
        available = [c["booth_number"] for c in companies]
        random.shuffle(available)

        solution = []
        time_used = 0

        for booth in available:
            # Estimate time for this booth
            visit_time = avg_interaction_time + 2.0  # +2 for travel

            if time_used + visit_time <= time_budget:
                solution.append(booth)
                time_used += visit_time

        return solution

    def _calculate_solution_score(self, solution: List[str]) -> float:
        """Calculate score of a solution."""
        # Placeholder - in real implementation, look up scores
        return len(solution) * 10.0

    def _generate_neighbor(
        self,
        solution: List[str],
        companies: List[Dict],
        time_budget: float,
        avg_interaction_time: float
    ) -> List[str]:
        """Generate neighbor solution by swapping or adding/removing booth."""
        neighbor = solution.copy()

        operation = random.choice(["swap", "add", "remove"])

        if operation == "swap" and len(neighbor) >= 2:
            i, j = random.sample(range(len(neighbor)), 2)
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]

        elif operation == "add":
            available_booths = [
                c["booth_number"] for c in companies
                if c["booth_number"] not in neighbor
            ]
            if available_booths:
                neighbor.append(random.choice(available_booths))

        elif operation == "remove" and len(neighbor) > 0:
            neighbor.pop(random.randint(0, len(neighbor) - 1))

        return neighbor

    def _tournament_select(
        self,
        population: List[List[str]],
        fitness_scores: List[float],
        tournament_size: int = 3
    ) -> List[str]:
        """Select individual using tournament selection."""
        indices = random.sample(range(len(population)), tournament_size)
        best_idx = max(indices, key=lambda i: fitness_scores[i])
        return population[best_idx]

    def _crossover(self, parent1: List[str], parent2: List[str]) -> List[str]:
        """Perform crossover between two parents."""
        # Order crossover
        if not parent1 or not parent2:
            return parent1 if len(parent1) > len(parent2) else parent2

        # Take first half from parent1, add missing from parent2
        split = len(parent1) // 2
        child = parent1[:split]

        for booth in parent2:
            if booth not in child:
                child.append(booth)

        return child

    def _mutate(
        self,
        individual: List[str],
        companies: List[Dict],
        time_budget: float,
        avg_interaction_time: float
    ) -> List[str]:
        """Mutate individual."""
        return self._generate_neighbor(
            individual,
            companies,
            time_budget,
            avg_interaction_time
        )

    def _build_ordered_route(
        self,
        booth_sequence: List[str],
        companies: List[Dict],
        start_location: str,
        avg_interaction_time: float
    ) -> List[Dict]:
        """Build ordered route from booth sequence."""
        route = []
        current = start_location
        cumulative_time = 0

        # Create booth to company mapping
        booth_to_company = {c["booth_number"]: c for c in companies}

        for booth in booth_sequence:
            # Calculate travel time
            if current == start_location:
                travel_time = 2.0
            else:
                try:
                    _, travel_time = self.graph.dijkstra_path(current, booth)
                except:
                    travel_time = 3.0

            company = booth_to_company.get(booth, {})

            route.append({
                "company_id": company.get("id", ""),
                "booth_number": booth,
                "travel_time": travel_time,
                "service_time": avg_interaction_time,
                "arrival_time": cumulative_time + travel_time,
                "score": company.get("score", 1.0)
            })

            cumulative_time += travel_time + avg_interaction_time
            current = booth

        return route
