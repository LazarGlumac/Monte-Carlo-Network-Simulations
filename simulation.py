import copy
from algorithms.mst import MST
from algorithms.shortest_path import shortest_path
from topologies.topology import (FullyConnectedTopology, ConstantTopology, ClusteredTopology)
import random
from scipy.stats import truncnorm
import plotly.express as px
import os

RESULTS_DIR = "results"

class Simulation():
    """
    A class to represent a simulation of a network topology
    """
    
    def __init__(self, num_sims, topology, graph_name) -> None:
        self.num_sims = num_sims
        self.topology = topology
        self.graph_name = graph_name
        self.original_graph = copy.deepcopy(topology.graph) # use deep copy to avoid copying by reference
        self.link_failure_samples = []
        self.mst_graph_result = []
        self.shortest_path_result = []

    def sample_truncated_normal(self, mean, sd, low, upp):
        return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

    def sample_link_failure(self):
        x = self.sample_truncated_normal(0.5, 0.5, 0, 1)
        link_failure = x.rvs()
        self.link_failure_samples.append(link_failure)
        
        for i in range(len(self.topology.graph)):
            for j in range(i):
                if (self.topology.graph[i][j] > 0):
                    if random.random() <= link_failure:
                        self.topology.destroy_link(i, j)
            
    def simulate_mst(self, original_mst):
        sampled_mst = MST(self.topology.graph)
        self.mst_graph_result.append(len(sampled_mst))
        
    def simulate_max_flow(self):
        pass

    def simulate_shortest_path(self, source, dest):
        path = shortest_path(self.topology.graph, source, dest)
        self.shortest_path_result.append(len(path))
        
    def simulate(self):
        # pick source and sink here?
        source = 0
        sink = 0

        # shortest path source and dest
        # TODO: should these be random or should we let the user specify?
        sp_source = random.randint(0, len(self.topology.graph)-1)
        sp_dest = random.randint(0, len(self.topology.graph)-1)
        
        # initial algorithm output on non-sampled graph
        original_mst = MST(self.original_graph)
        original_max_flow = 0
        original_shortest_path = 0
        
        for i in range(self.num_sims):
            self.sample_link_failure()
            self.simulate_mst(original_mst)
            self.simulate_max_flow()
            self.simulate_shortest_path(sp_source, sp_dest)
            self.topology.graph = copy.deepcopy(self.original_graph) # use deep copy to avoid copying by reference
            
    def visualize_mst(self):
        fig = px.scatter(x=self.link_failure_samples, y=self.mst_graph_result, title=self.graph_name + " - # nodes reachable in the network")
        fig.write_image(os.path.join(RESULTS_DIR, self.graph_name + "_MST.png") )

    def visualize_max_flow(self):
        pass
    
    def visualize_shortest_path(self):
        fig = px.density_heatmap(x=self.link_failure_samples,
                                 y=self.shortest_path_result, title=self.graph_name + " - Link Failure Rate VS Shortest Path Length",
                                 labels={
                                        "x": "Link failure probability",
                                        "y": "Length of shortest path"
                                 })
        fig.write_image(os.path.join(RESULTS_DIR, self.graph_name + "_SP.png") )
    
    def visualize_simulation(self):
        self.visualize_mst()
        self.visualize_max_flow()
        self.visualize_shortest_path()

class FullyConnectedTopologySimulation(Simulation):
    def __init__(self, num_sims, num_nodes) -> None:
        topology = FullyConnectedTopology(num_nodes)
        super().__init__(num_sims, topology, "Fully_Connected_Topology")
    
class ConstantTopologySimulation(Simulation):
    def __init__(self, num_sims, num_nodes, links_per_node) -> None:
        topology = ConstantTopology(num_nodes, links_per_node)
        super().__init__(num_sims, topology, "Constant_Topology")
        
class ClusteredTopologySimulation(Simulation):
    def __init__(self, num_sims, num_nodes, num_clusters) -> None:
        topology = ClusteredTopology(num_nodes, num_clusters)
        super().__init__(num_sims, topology, "Clustered_Topology")

NUM_SIMS = 100
NUM_NODES = 60
FullyConnectedTopologySimulation = FullyConnectedTopologySimulation(NUM_SIMS, NUM_NODES)
FullyConnectedTopologySimulation.simulate()
FullyConnectedTopologySimulation.visualize_simulation()

NUM_LINKS_PER_NODE = 15
ConstantTopologySimulation = ConstantTopologySimulation(NUM_SIMS, NUM_NODES, NUM_LINKS_PER_NODE)
ConstantTopologySimulation.simulate()
ConstantTopologySimulation.visualize_simulation()

NUM_CLUSTERS = 12
ClusteredTopologySimulation = ClusteredTopologySimulation(NUM_SIMS, NUM_NODES, NUM_CLUSTERS)
ClusteredTopologySimulation.simulate()
ClusteredTopologySimulation.visualize_simulation()