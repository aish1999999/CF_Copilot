"""
Graph builder service for routing optimization.

Builds a graph from booth coordinates and computes shortest paths.
"""
import networkx as nx
from typing import Dict, List, Tuple
from math import sqrt


class GraphBuilder:
    """Build and manage the career fair floor plan graph."""

    def __init__(self, avg_walking_speed_mps: float = 1.4):
        """
        Initialize graph builder.

        Args:
            avg_walking_speed_mps: Average walking speed in meters per second
        """
        self.graph = nx.Graph()
        self.walking_speed = avg_walking_speed_mps

    def calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Calculate Euclidean distance between two coordinates.

        Args:
            coord1: (x, y) coordinates of first point
            coord2: (x, y) coordinates of second point

        Returns:
            Distance in meters
        """
        x1, y1 = coord1
        x2, y2 = coord2
        return sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def calculate_travel_time(self, distance: float) -> float:
        """
        Calculate travel time based on distance.

        Args:
            distance: Distance in meters

        Returns:
            Travel time in minutes
        """
        time_seconds = distance / self.walking_speed
        return time_seconds / 60.0  # Convert to minutes

    def add_booth(self, booth_id: str, x: float, y: float, ballroom: str):
        """
        Add a booth node to the graph.

        Args:
            booth_id: Booth identifier
            x: X coordinate
            y: Y coordinate
            ballroom: Ballroom name
        """
        self.graph.add_node(
            booth_id,
            pos=(x, y),
            ballroom=ballroom,
            type="booth"
        )

    def add_entrance(self, entrance_id: str, x: float, y: float, ballroom: str):
        """Add an entrance/exit node to the graph."""
        self.graph.add_node(
            entrance_id,
            pos=(x, y),
            ballroom=ballroom,
            type="entrance"
        )

    def connect_booths_in_ballroom(self):
        """
        Connect all booths within the same ballroom.

        Creates edges between all booths in the same ballroom with travel time weights.
        """
        # Group nodes by ballroom
        ballroom_nodes = {}
        for node, data in self.graph.nodes(data=True):
            ballroom = data.get("ballroom")
            if ballroom not in ballroom_nodes:
                ballroom_nodes[ballroom] = []
            ballroom_nodes[ballroom].append(node)

        # Connect all nodes within same ballroom
        for ballroom, nodes in ballroom_nodes.items():
            for i, node1 in enumerate(nodes):
                for node2 in nodes[i+1:]:
                    pos1 = self.graph.nodes[node1]["pos"]
                    pos2 = self.graph.nodes[node2]["pos"]

                    distance = self.calculate_distance(pos1, pos2)
                    travel_time = self.calculate_travel_time(distance)

                    self.graph.add_edge(
                        node1,
                        node2,
                        weight=travel_time,
                        distance=distance
                    )

    def dijkstra_path(self, start: str, end: str) -> Tuple[List[str], float]:
        """
        Find shortest path between two nodes using Dijkstra's algorithm.

        Args:
            start: Start node ID
            end: End node ID

        Returns:
            Tuple of (path, total_travel_time)
        """
        try:
            path = nx.dijkstra_path(self.graph, start, end, weight="weight")
            travel_time = nx.dijkstra_path_length(self.graph, start, end, weight="weight")
            return path, travel_time
        except nx.NetworkXNoPath:
            return [], float('inf')

    def get_all_pairwise_distances(self, nodes: List[str]) -> Dict[Tuple[str, str], float]:
        """
        Compute all pairwise shortest path distances for given nodes.

        Args:
            nodes: List of node IDs

        Returns:
            Dictionary mapping (node1, node2) to travel time
        """
        distances = {}
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                _, travel_time = self.dijkstra_path(node1, node2)
                distances[(node1, node2)] = travel_time
                distances[(node2, node1)] = travel_time

        return distances

    def build_from_booths(self, booths: List[Dict]):
        """
        Build graph from a list of booth dictionaries.

        Args:
            booths: List of booth data with keys: booth_number, coordinate_x, coordinate_y, ballroom
        """
        # Add all booths as nodes
        for booth in booths:
            if booth.get("coordinate_x") is not None and booth.get("coordinate_y") is not None:
                self.add_booth(
                    booth["booth_number"],
                    booth["coordinate_x"],
                    booth["coordinate_y"],
                    booth["ballroom"]
                )

        # Connect booths within ballrooms
        self.connect_booths_in_ballroom()

    def get_graph_info(self) -> Dict:
        """Get information about the graph."""
        return {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "ballrooms": list(set(data.get("ballroom") for _, data in self.graph.nodes(data=True))),
        }
