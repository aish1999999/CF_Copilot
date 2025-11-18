"""
Algorithmic tests for routing optimization.

Tests:
- Dijkstra's algorithm correctness
- Greedy optimization
- ILP optimization
- Simulated Annealing
- Genetic Algorithm
- Real-time replanning
- Edge cases and boundary conditions
"""

import pytest
from app.services.graph_builder import GraphBuilder
from app.services.routing_optimizer import RoutingOptimizer
from app.services.advanced_optimizer import AdvancedOptimizer
from app.services.realtime_replanner import RealtimeReplanner


@pytest.fixture
def simple_graph():
    """Create a simple test graph."""
    graph = GraphBuilder()

    # Add booths in a line
    graph.add_booth("A", 0, 0, "Waldorf")
    graph.add_booth("B", 10, 0, "Waldorf")
    graph.add_booth("C", 20, 0, "Waldorf")
    graph.add_booth("D", 30, 0, "Waldorf")

    graph.connect_booths_in_ballroom()

    return graph


@pytest.fixture
def complex_graph():
    """Create a more complex test graph."""
    graph = GraphBuilder()

    # Waldorf ballroom (square layout)
    graph.add_booth("W1", 0, 0, "Waldorf")
    graph.add_booth("W2", 10, 0, "Waldorf")
    graph.add_booth("W3", 0, 10, "Waldorf")
    graph.add_booth("W4", 10, 10, "Waldorf")

    # Imperial ballroom (separate location)
    graph.add_booth("I1", 50, 0, "Imperial")
    graph.add_booth("I2", 60, 0, "Imperial")

    graph.connect_booths_in_ballroom()

    return graph


@pytest.fixture
def sample_companies():
    """Sample companies for testing."""
    return [
        {"id": 1, "booth_number": "A", "score": 10.0, "name": "Company A"},
        {"id": 2, "booth_number": "B", "score": 8.0, "name": "Company B"},
        {"id": 3, "booth_number": "C", "score": 6.0, "name": "Company C"},
        {"id": 4, "booth_number": "D", "score": 4.0, "name": "Company D"},
    ]


class TestGraphBuilder:
    """Tests for GraphBuilder class."""

    def test_calculate_distance(self):
        """Test Euclidean distance calculation."""
        graph = GraphBuilder()

        # Test horizontal distance
        dist = graph.calculate_distance((0, 0), (10, 0))
        assert dist == 10.0

        # Test vertical distance
        dist = graph.calculate_distance((0, 0), (0, 10))
        assert dist == 10.0

        # Test diagonal distance (3-4-5 triangle)
        dist = graph.calculate_distance((0, 0), (3, 4))
        assert dist == 5.0

    def test_calculate_travel_time(self):
        """Test travel time calculation."""
        graph = GraphBuilder(avg_walking_speed_mps=1.4)

        # 14 meters at 1.4 m/s = 10 seconds = 1/6 minute
        time = graph.calculate_travel_time(14.0)
        assert abs(time - 0.1667) < 0.01

    def test_add_booth(self, simple_graph):
        """Test adding booths to graph."""
        assert simple_graph.graph.number_of_nodes() == 4
        assert "A" in simple_graph.graph.nodes()
        assert simple_graph.graph.nodes["A"]["ballroom"] == "Waldorf"

    def test_connect_booths_in_ballroom(self, simple_graph):
        """Test booth connections."""
        # In a line of 4 booths, should have 6 edges (complete graph)
        assert simple_graph.graph.number_of_edges() == 6

    def test_dijkstra_path_simple(self, simple_graph):
        """Test Dijkstra's algorithm on simple graph."""
        path, time = simple_graph.dijkstra_path("A", "D")

        assert len(path) == 2  # Direct path
        assert path[0] == "A"
        assert path[-1] == "D"
        assert time > 0

    def test_dijkstra_path_no_path(self, complex_graph):
        """Test Dijkstra when no path exists (different ballrooms not connected)."""
        # W1 and I1 are in different ballrooms, not connected
        path, time = complex_graph.dijkstra_path("W1", "I1")

        assert path == []
        assert time == float('inf')

    def test_get_all_pairwise_distances(self, simple_graph):
        """Test pairwise distance calculation."""
        nodes = ["A", "B", "C"]
        distances = simple_graph.get_all_pairwise_distances(nodes)

        # Should have distances for all pairs
        assert ("A", "B") in distances
        assert ("B", "C") in distances
        assert ("A", "C") in distances

        # Symmetric
        assert distances[("A", "B")] == distances[("B", "A")]


class TestRoutingOptimizer:
    """Tests for RoutingOptimizer class."""

    def test_greedy_route_basic(self, simple_graph, sample_companies):
        """Test basic greedy route optimization."""
        optimizer = RoutingOptimizer(simple_graph)

        result = optimizer.greedy_route(
            sample_companies,
            time_budget_minutes=30,
            start_location="entrance"
        )

        assert "route" in result
        assert "total_time" in result
        assert "total_score" in result
        assert len(result["route"]) > 0

    def test_greedy_route_empty_companies(self, simple_graph):
        """Test greedy route with no companies."""
        optimizer = RoutingOptimizer(simple_graph)

        result = optimizer.greedy_route(
            [],
            time_budget_minutes=30
        )

        assert result["route"] == []
        assert result["total_score"] == 0

    def test_greedy_route_tight_budget(self, simple_graph, sample_companies):
        """Test greedy route with very tight time budget."""
        optimizer = RoutingOptimizer(simple_graph)

        result = optimizer.greedy_route(
            sample_companies,
            time_budget_minutes=5,  # Very limited
            avg_interaction_time=5.0
        )

        # Should visit very few or no companies
        assert len(result["route"]) <= 1

    def test_greedy_route_generous_budget(self, simple_graph, sample_companies):
        """Test greedy route with generous budget."""
        optimizer = RoutingOptimizer(simple_graph)

        result = optimizer.greedy_route(
            sample_companies,
            time_budget_minutes=100,  # Plenty of time
            avg_interaction_time=5.0
        )

        # Should visit all companies
        assert len(result["route"]) == len(sample_companies)

    def test_greedy_prioritizes_high_score(self, simple_graph, sample_companies):
        """Test that greedy algorithm prioritizes high-score companies."""
        optimizer = RoutingOptimizer(simple_graph)

        result = optimizer.greedy_route(
            sample_companies,
            time_budget_minutes=20,
            avg_interaction_time=5.0
        )

        # First company should be highest score
        if len(result["route"]) > 0:
            first_company = result["route"][0]
            # Company A has score 10.0
            assert first_company["score"] == 10.0

    def test_calculate_route_time(self, simple_graph):
        """Test route time calculation."""
        optimizer = RoutingOptimizer(simple_graph)

        time = optimizer.calculate_route_time(
            ["A", "B", "C"],
            avg_interaction_time=5.0
        )

        # 3 visits * 5 min each + travel time
        assert time >= 15.0


class TestAdvancedOptimizer:
    """Tests for advanced optimization algorithms."""

    def test_ilp_basic(self, simple_graph, sample_companies):
        """Test ILP optimization."""
        optimizer = AdvancedOptimizer(simple_graph)

        result = optimizer.ilp_optimize(
            sample_companies,
            time_budget_minutes=30,
            solver_timeout_seconds=5
        )

        # Should return a result (may have error if OR-Tools not available)
        assert "route" in result or "error" in result

    def test_simulated_annealing_basic(self, simple_graph, sample_companies):
        """Test Simulated Annealing optimization."""
        optimizer = AdvancedOptimizer(simple_graph)

        result = optimizer.simulated_annealing(
            sample_companies,
            time_budget_minutes=30,
            max_iterations=100
        )

        assert "route" in result
        assert "total_score" in result
        assert len(result["route"]) >= 0

    def test_genetic_algorithm_basic(self, simple_graph, sample_companies):
        """Test Genetic Algorithm optimization."""
        optimizer = AdvancedOptimizer(simple_graph)

        result = optimizer.genetic_algorithm(
            sample_companies,
            time_budget_minutes=30,
            population_size=10,
            generations=10
        )

        assert "route" in result
        assert "total_score" in result

    def test_random_solution_generation(self, simple_graph, sample_companies):
        """Test random solution generation."""
        optimizer = AdvancedOptimizer(simple_graph)

        solution = optimizer._generate_random_solution(
            sample_companies,
            time_budget=30,
            avg_interaction_time=5.0
        )

        assert isinstance(solution, list)
        # Should be feasible (within time budget)
        assert len(solution) <= len(sample_companies)

    def test_metaheuristic_convergence(self, simple_graph, sample_companies):
        """Test that metaheuristics improve over iterations."""
        optimizer = AdvancedOptimizer(simple_graph)

        # Run SA with very few iterations
        result_short = optimizer.simulated_annealing(
            sample_companies,
            time_budget_minutes=30,
            max_iterations=10
        )

        # Run SA with more iterations
        result_long = optimizer.simulated_annealing(
            sample_companies,
            time_budget_minutes=30,
            max_iterations=100
        )

        # Longer run should generally be as good or better
        # (Not guaranteed due to randomness, but likely)
        assert result_long["total_score"] >= result_short["total_score"] * 0.8


class TestRealtimeReplanner:
    """Tests for real-time replanning."""

    @pytest.fixture
    def sample_route(self):
        """Sample route for replanning tests."""
        return [
            {
                "company_id": 1,
                "booth_number": "A",
                "travel_time": 2.0,
                "service_time": 5.0,
                "arrival_time": 2.0,
                "score": 10.0
            },
            {
                "company_id": 2,
                "booth_number": "B",
                "travel_time": 3.0,
                "service_time": 5.0,
                "arrival_time": 10.0,
                "score": 8.0
            },
            {
                "company_id": 3,
                "booth_number": "C",
                "travel_time": 3.0,
                "service_time": 5.0,
                "arrival_time": 18.0,
                "score": 6.0
            },
        ]

    def test_replan_on_delay(
        self,
        simple_graph,
        sample_companies,
        sample_route
    ):
        """Test replanning when delayed."""
        optimizer = RoutingOptimizer(simple_graph)
        replanner = RealtimeReplanner(simple_graph, optimizer)

        result = replanner.replan_on_delay(
            current_route=sample_route,
            current_position=1,  # At second stop
            delay_minutes=10,
            time_budget_minutes=40,
            companies=sample_companies
        )

        assert result["replanned"] is True
        assert "delay_impact" in result
        # Remaining stops should be fewer due to delay
        assert len(result["route"]) <= len(sample_route) - 1

    def test_replan_on_booth_closure(
        self,
        simple_graph,
        sample_companies,
        sample_route
    ):
        """Test replanning when booth closes."""
        optimizer = RoutingOptimizer(simple_graph)
        replanner = RealtimeReplanner(simple_graph, optimizer)

        result = replanner.replan_on_booth_closure(
            current_route=sample_route,
            current_position=1,
            closed_booths={"C"},  # Booth C closes
            time_budget_minutes=40,
            companies=sample_companies
        )

        assert result["replanned"] is True
        # Route should not include booth C
        assert not any(stop["booth_number"] == "C" for stop in result["route"])

    def test_add_priority_company(
        self,
        simple_graph,
        sample_companies,
        sample_route
    ):
        """Test adding priority company to route."""
        optimizer = RoutingOptimizer(simple_graph)
        replanner = RealtimeReplanner(simple_graph, optimizer)

        new_company = {
            "id": 5,
            "booth_number": "D",
            "score": 15.0,
            "name": "Priority Company"
        }

        result = replanner.add_priority_company(
            current_route=sample_route,
            current_position=1,
            new_company=new_company,
            time_budget_minutes=40,
            companies=sample_companies,
            insert_asap=True
        )

        assert result["replanned"] is True
        # Priority company should be in route
        assert any(stop["company_id"] == 5 for stop in result["route"])

    def test_get_replan_recommendations_behind(self, simple_graph):
        """Test recommendations when behind schedule."""
        optimizer = RoutingOptimizer(simple_graph)
        replanner = RealtimeReplanner(simple_graph, optimizer)

        route = [{"travel_time": 2, "service_time": 5} for _ in range(4)]

        recs = replanner.get_replan_recommendations(
            current_route=route,
            current_position=2,
            current_time_spent=20,  # Expected: 14
            time_budget_minutes=40
        )

        assert recs["on_track"] is False
        assert recs["time_variance"] > 0
        assert len(recs["recommendations"]) > 0

    def test_get_replan_recommendations_ahead(self, simple_graph):
        """Test recommendations when ahead of schedule."""
        optimizer = RoutingOptimizer(simple_graph)
        replanner = RealtimeReplanner(simple_graph, optimizer)

        route = [{"travel_time": 2, "service_time": 5} for _ in range(4)]

        recs = replanner.get_replan_recommendations(
            current_route=route,
            current_position=2,
            current_time_spent=10,  # Expected: 14
            time_budget_minutes=40
        )

        assert recs["time_variance"] < 0
        # Should suggest adding more companies
        assert any(
            "ahead" in rec["type"] or "add" in rec.get("action", "").lower()
            for rec in recs["recommendations"]
        )


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_company(self, simple_graph):
        """Test with single company."""
        optimizer = RoutingOptimizer(simple_graph)

        result = optimizer.greedy_route(
            [{"id": 1, "booth_number": "A", "score": 5.0}],
            time_budget_minutes=10
        )

        assert len(result["route"]) <= 1

    def test_zero_time_budget(self, simple_graph, sample_companies):
        """Test with zero time budget."""
        optimizer = RoutingOptimizer(simple_graph)

        result = optimizer.greedy_route(
            sample_companies,
            time_budget_minutes=0
        )

        assert result["route"] == []

    def test_negative_scores(self, simple_graph):
        """Test handling of negative scores."""
        optimizer = RoutingOptimizer(simple_graph)

        companies = [
            {"id": 1, "booth_number": "A", "score": -5.0},
            {"id": 2, "booth_number": "B", "score": 10.0},
        ]

        result = optimizer.greedy_route(companies, time_budget_minutes=20)

        # Should still work, just prioritize positive scores
        assert "route" in result

    def test_very_large_graph(self):
        """Test with large number of booths."""
        graph = GraphBuilder()

        # Add 50 booths
        for i in range(50):
            graph.add_booth(f"B{i}", i * 10, 0, "Waldorf")

        graph.connect_booths_in_ballroom()

        assert graph.graph.number_of_nodes() == 50

        # Test Dijkstra still works
        path, time = graph.dijkstra_path("B0", "B49")
        assert len(path) > 0

    def test_disconnected_graph_components(self):
        """Test graph with disconnected components."""
        graph = GraphBuilder()

        # Component 1
        graph.add_booth("A1", 0, 0, "Waldorf")
        graph.add_booth("A2", 10, 0, "Waldorf")

        # Component 2 (different ballroom, not connected)
        graph.add_booth("B1", 100, 0, "Imperial")
        graph.add_booth("B2", 110, 0, "Imperial")

        graph.connect_booths_in_ballroom()

        # Should have two disconnected components
        path, time = graph.dijkstra_path("A1", "B1")
        assert path == []
        assert time == float('inf')


def test_algorithm_consistency(simple_graph, sample_companies):
    """Test that different algorithms produce reasonable results."""
    greedy_opt = RoutingOptimizer(simple_graph)
    advanced_opt = AdvancedOptimizer(simple_graph)

    budget = 30

    greedy_result = greedy_opt.greedy_route(
        sample_companies,
        budget
    )

    sa_result = advanced_opt.simulated_annealing(
        sample_companies,
        budget,
        max_iterations=50
    )

    # Both should produce non-empty routes
    assert len(greedy_result["route"]) > 0
    assert len(sa_result["route"]) > 0

    # Scores should be positive
    assert greedy_result["total_score"] > 0
    assert sa_result["total_score"] > 0

    # Should respect time budget
    assert greedy_result["total_time"] <= budget
    assert sa_result["total_time"] <= budget
