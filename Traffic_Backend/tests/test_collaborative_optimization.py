import networkx as nx
import unittest

class TrafficNetwork:
    """
    Simulates the shared state (The Graph) that both services interact with.
    In the real architecture, this would be the NetworkX graph loaded in memory.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self._initialize_mock_network()

    def _initialize_mock_network(self):
        # 1. Primary Route (Route A): Direct, short path
        # Length: 5km. This is the preferred route initially.
        self.graph.add_edge("Start", "End", weight=5.0, id="Route_A")

        # 2. Alternative Route (Route B): Indirect, longer path
        # Length: 10km + 10km = 20km.
        self.graph.add_edge("Start", "Intermediate", weight=10.0, id="Route_B1")
        self.graph.add_edge("Intermediate", "End", weight=10.0, id="Route_B2")

class RoutingService:
    """
    Responsible for calculating paths based on current network state.
    """
    def __init__(self, network: TrafficNetwork):
        self.network = network

    def get_optimal_route(self, start_node, end_node):
        try:
            # Uses Dijkstra's algorithm to find the path with lowest weight (cost)
            path = nx.dijkstra_path(self.network.graph, start_node, end_node, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return None

class ProjectService:
    """
    Responsible for managing construction projects.
    Implements the 'Collaborative Optimization' logic by modifying graph weights.
    """
    def __init__(self, network: TrafficNetwork):
        self.network = network

    def create_project(self, edge_u, edge_v, project_type):
        """
        When a project is created, it acts as a capacity-reducing event.
        The edge weight is updated to reflect this closure/restriction.
        """
        print(f"\n[Project Service] Creating '{project_type}' on segment {edge_u}->{edge_v}...")
        
        if self.network.graph.has_edge(edge_u, edge_v):
            # Research Logic: Construction = Infinite Cost (or very high penalty)
            # This forces the routing algorithm to look elsewhere.
            self.network.graph[edge_u][edge_v]['weight'] = float('inf')
            print(f"[Project Service] ALERT: Segment {edge_u}->{edge_v} weight updated to INFINITY.")
        else:
            print("[Project Service] Error: Segment not found.")

class TestCollaborativeOptimization(unittest.TestCase):
    """
    Test Scenario as defined in Strategy Section 7.1
    """
    def setUp(self):
        # Initialize the shared network and services
        self.network = TrafficNetwork()
        self.router = RoutingService(self.network)
        self.project_manager = ProjectService(self.network)

    def test_project_triggers_rerouting(self):
        start = "Start"
        end = "End"

        # 1. Baseline Check
        # Before the project, the router should pick the direct path (Route A)
        initial_route = self.router.get_optimal_route(start, end)
        print(f"\n[1] Initial Route Calculated: {initial_route}")
        
        # Assert initial state is correct (Direct path)
        self.assertEqual(initial_route, ["Start", "End"], "Initial route should be the direct path.")

        # 2. Trigger Event: User adds a project
        self.project_manager.create_project("Start", "End", "Resurfacing Project")

        # 3. Re-run Routing
        # The router queries the SAME network instance, which now has updated weights
        new_route = self.router.get_optimal_route(start, end)
        print(f"[2] New Route Calculated: {new_route}")

        # 4. Collaborative Optimization Assertion
        # The new route MUST differ from the initial route.
        # It should now take the alternative path via "Intermediate".
        self.assertNotEqual(initial_route, new_route, "Traffic failed to divert! Route is unchanged.")
        self.assertEqual(new_route, ["Start", "Intermediate", "End"], "Traffic did not take the expected alternative.")
        
        print("\n[SUCCESS] System correctly optimized traffic flow around the construction project.")

if __name__ == "__main__":
    unittest.main()