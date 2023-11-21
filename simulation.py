import copy
from algorithms.mst import MST
from algorithms.shortest_path import shortest_path
from algorithms.find_disconnected_components import find_num_components
from topologies.topology import (FullyConnectedTopology, ConstantTopology, ClusteredTopology)
import random
from scipy.stats import truncnorm
import plotly.express as px
import os
from abc import ABC, abstractmethod

RESULTS_DIR = "results"
MIN_NODES = 25
MAX_NODES = 150
MIN_CLUSTERS = 5
MAX_CLUSTERS = 15

class Simulation(ABC):
    """
    A class to represent a simulation of a network topology
    """
    
    def __init__(self, num_sims, topology, graph_name, randomize_num_nodes) -> None:
        self.num_sims = num_sims
        self.randomize_num_nodes = randomize_num_nodes
        self.graph_name = graph_name
        self.link_failure_samples = []
        self.mst_graph_result = []
        self.shortest_path_result = []
        self.disconnected_components_result = []
        
        if randomize_num_nodes:
            self.topology = self.generate_topology()
        else:
            self.topology = topology
        
        # keep a list of the original graphs before sampling the link failure in case it is needed for analysis
        # if randomize_num_nodes is false, this list will only contain one graph
        self.original_graphs = [copy.deepcopy(self.topology.graph)] # use deep copy to avoid copying by reference

    @abstractmethod
    def generate_topology(self):
        pass
    
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
            
    def simulate_mst(self):
        sampled_mst = MST(self.topology.graph)
        if self.randomize_num_nodes:
            self.mst_graph_result.append((len(sampled_mst), len(self.topology.graph)))
        else:
            self.mst_graph_result.append(len(sampled_mst))
            
    def simulate_disconnected_components(self):
        sampled_disc_components = find_num_components(self.topology.graph)
        self.disconnected_components_result.append(sampled_disc_components)
        
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
        
        for i in range(self.num_sims):
            self.sample_link_failure()
            self.simulate_mst()
            self.simulate_disconnected_components()
            self.simulate_max_flow()
            self.simulate_shortest_path(sp_source, sp_dest)
            
            if self.randomize_num_nodes:
                self.topology = self.generate_topology()
                self.original_graphs.append(copy.deepcopy(self.topology.graph))
            else:
                self.topology.graph = copy.deepcopy(self.original_graphs[0]) # use deep copy to avoid copying by reference
            
    def visualize_mst(self):
        graph_title = "Nodes Reachable In A " + self.graph_name
        
        if self.randomize_num_nodes:
            reachable_nodes = [mst_result[0] for mst_result in self.mst_graph_result]
            total_nodes = [mst_result[1] for mst_result in self.mst_graph_result]
            fig = px.scatter_3d(x=self.link_failure_samples, y=reachable_nodes, z=total_nodes, title=graph_title)
        else:
            fig = px.scatter(x=self.link_failure_samples, y=self.mst_graph_result, title=graph_title)
        
        fig.write_image(os.path.join(RESULTS_DIR, self.graph_name + "_MST.png"))

    def visualize_disconnected_components(self):
        graph_title = "Number of disconncted components in a " + self.graph_name
        fig = px.scatter(x=self.link_failure_samples, y=self.disconnected_components_result, title=graph_title)
        fig.write_image(os.path.join(RESULTS_DIR, self.graph_name + "_MST.png"))

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
        self.visualize_disconnected_components()
        self.visualize_max_flow()
        self.visualize_shortest_path()

class FullyConnectedTopologySimulation(Simulation):
    """
    A child class of Simulation to simulate Fully Connected Topologies
    
    If num_nodes equals -1, it will randomize the topology in each individual simulation.
    Otherwise, it creates a topology from the given num_nodes and use that for every simulation.
    """
    
    def __init__(self, num_sims, num_nodes) -> None:
        randomize_num_nodes = num_nodes < 1
        topology = None
        if not randomize_num_nodes:
            topology = FullyConnectedTopology(num_nodes)
            
        super().__init__(num_sims, topology, "Fully_Connected_Topology", randomize_num_nodes)
        
    def generate_topology(self):
        num_nodes = random.randint(MIN_NODES, MAX_NODES)
        return FullyConnectedTopology(num_nodes)
    
class ConstantTopologySimulation(Simulation):
    """
    A child class of Simulation to simulate Constant Topologies
    
    If num_nodes or links_per_node  equals -1, it will randomize the topology in each individual simulation.
    Otherwise, it creates a topology from the given num_nodes and links_per_node and use that for every simulation.
    """
    
    def __init__(self, num_sims, num_nodes, links_per_node) -> None:
        randomize_num_nodes = num_nodes < 1 or links_per_node < 1
        topology = None
        if not randomize_num_nodes:
            topology = ConstantTopology(num_nodes, links_per_node)
            
        super().__init__(num_sims, topology, "Constant_Topology", randomize_num_nodes)
        
    def generate_topology(self):
        num_nodes = random.randint(MIN_NODES, MAX_NODES)
        links_per_node = random.randint(MIN_NODES-1, num_nodes-1)
        return ConstantTopology(num_nodes, links_per_node)
        
class ClusteredTopologySimulation(Simulation):
    """
    A child class of Simulation to simulate Clustered Topologies.
    
    If num_nodes or num_clusters equals -1, it will randomize the topology in each individual simulation.
    Otherwise, it creates a topology from the given num_nodes and num_clusters and use that for every simulation.
    """
    
    def __init__(self, num_sims, num_nodes, num_clusters) -> None:
        randomize_num_nodes = num_nodes < 1 or num_clusters < 1
        topology = None
        if not randomize_num_nodes:
            topology = ClusteredTopology(num_nodes, num_clusters)
         
        super().__init__(num_sims, topology, "Clustered_Topology", randomize_num_nodes)
        
    def generate_topology(self):
        num_clusters = random.randint(MIN_CLUSTERS, MAX_CLUSTERS)
        num_nodes = num_clusters * random.randint(MIN_NODES // MIN_CLUSTERS, MAX_NODES // MAX_CLUSTERS)
        return ClusteredTopology(num_nodes, num_clusters)

NUM_SIMS = 100
NUM_NODES = 50
NUM_CLUSTERS = 10
NUM_LINKS_PER_NODE = -1

FullyConnectedTopologySimulation = FullyConnectedTopologySimulation(NUM_SIMS, NUM_NODES)
FullyConnectedTopologySimulation.simulate()
FullyConnectedTopologySimulation.visualize_simulation()

# sometimtes creating constant topology errors, so this is commented out until that gets fixed

# ConstantTopologySimulation = ConstantTopologySimulation(NUM_SIMS, NUM_NODES, NUM_LINKS_PER_NODE)
# ConstantTopologySimulation.simulate()
# ConstantTopologySimulation.visualize_simulation()

ClusteredTopologySimulation = ClusteredTopologySimulation(NUM_SIMS, NUM_NODES, NUM_CLUSTERS)
ClusteredTopologySimulation.simulate()
ClusteredTopologySimulation.visualize_simulation()