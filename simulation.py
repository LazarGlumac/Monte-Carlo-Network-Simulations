import copy
from algorithms.mst import MST
from topologies.topology import (FullyConnectedTopology, ConstantTopology, ClusteredTopology)
import random
from scipy.stats import truncnorm
import plotly.graph_objects as go
import plotly.io as pio

class Simulation():
    """
    A class to represent a simulation of a network topology
    """
    
    def __init__(self, num_sims, topology, graph_name) -> None:
        self.num_sims = num_sims
        self.topology = topology
        self.graph_name = graph_name
        self.original_graph = copy.deepcopy(topology.graph) # use deep copy to avoid copying by reference
        self.mst_graph_result = []

    def sample_truncated_normal(self, mean, sd, low, upp):
        return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

    def SampleLinkFailure(self):
        x = self.sample_truncated_normal(0.5, 0.5, 0, 1)
        link_failure = x.rvs()
        
        for i in range(len(self.topology.graph)):
            for j in range(i):
                if (self.topology.graph[i][j] > 0):
                    if random.random() < link_failure:
                        self.topology.destroy_link(i, j)
                        self.topology.destroy_link(j, i)
            
    def SimulateMST(self, original_mst):
        sampled_mst = MST(self.topology.graph)
        self.mst_graph_result.append(len(sampled_mst))
        
    def SimulateMaxFlow(self):
        pass
    
    def SimulateShortestPath(self):
        pass
        
    def Simulate(self):
        # pick source and sink here?
        source = 0
        sink = 0
        
        # initial algorithm output on non-sampled graph
        original_mst = MST(self.original_graph)
        original_max_flow = 0
        original_shortest_path = 0
        
        for i in range(self.num_sims):
            self.SampleLinkFailure()
            self.SimulateMST(original_mst)
            self.SimulateMaxFlow()
            self.SimulateShortestPath()
            self.topology.graph = copy.deepcopy(self.original_graph) # use deep copy to avoid copying by reference
            
    def VisualizeMST(self):
        self.mst_graph_result.sort()
        
        png_renderer = pio.renderers["png"]
        png_renderer.width = 800
        png_renderer.height = 800

        pio.renderers.default = "png"

        fig = go.Figure(
            data=[go.Bar(y=self.mst_graph_result)],
            layout_title_text=self.graph_name + " - # nodes reachable in the network"
        )
        fig.write_image(self.graph_name + "_MST.png")

    def VisualizeMaxFlow(self):
        pass
    
    def VisualizeShortestPath(self):
        pass        
    
    def VisualizeSimulation(self):
        self.VisualizeMST()
        self.VisualizeMaxFlow()
        self.VisualizeShortestPath()

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
FullyConnectedTopologySimulation.Simulate()
FullyConnectedTopologySimulation.VisualizeSimulation()

NUM_LINKS_PER_NODE = 15
ConstantTopologySimulation = ConstantTopologySimulation(NUM_SIMS, NUM_NODES, NUM_LINKS_PER_NODE)
ConstantTopologySimulation.Simulate()
ConstantTopologySimulation.VisualizeSimulation()

NUM_CLUSTERS = 12
ClusteredTopologySimulation = ClusteredTopologySimulation(NUM_SIMS, NUM_NODES, NUM_CLUSTERS)
ClusteredTopologySimulation.Simulate()
ClusteredTopologySimulation.VisualizeSimulation()