import copy
import time
from algorithms.shortest_path import shortest_path
from algorithms.find_disconnected_components import find_num_components
from algorithms.max_flow import max_flow
from topologies.topology import (FullyConnectedTopology, ConstantTopology, ClusteredTopology)
import random
from scipy.stats import truncnorm
import plotly.express as px
import plotly.graph_objects as go
import os
from abc import ABC, abstractmethod
from progress.bar import Bar

RESULTS_DIR = {
    "max_flow": "results/max_flow",
    "disconnected_components": "results/disconnected_components",
    "shortest_path": "results/shortest_path"
}
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
        self.shortest_path_result = []
        self.max_flow_result = []
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
        link_failure = round(x.rvs(), 2)
        self.link_failure_samples.append(link_failure)
        
        for i in range(len(self.topology.graph)):
            for j in range(i):
                if (self.topology.graph[i][j] > 0):
                    if random.random() <= link_failure:
                        self.topology.destroy_link(i, j)
            
    def simulate_disconnected_components(self):
        sampled_disc_components = find_num_components(self.topology.graph)
        if self.randomize_num_nodes:
            self.disconnected_components_result.append((sampled_disc_components, len(self.topology.graph)))
        else:
            self.disconnected_components_result.append(sampled_disc_components)
        
    def simulate_max_flow(self, source, sink):
        sampled_max_flow = max_flow(self.topology.graph, source, sink)
        if self.randomize_num_nodes:
            self.max_flow_result.append((sampled_max_flow, len(self.topology.graph)))
        else:
            self.max_flow_result.append(sampled_max_flow)
    
    def simulate_shortest_path(self, source, dest):
        path, weight = shortest_path(self.topology.graph, source, dest)
        path_length = len(path) - 1
        if path == []:
            path_length = 0
        if (self.randomize_num_nodes):
            self.shortest_path_result.append((weight, len(self.topology.graph)))
        else:
            self.shortest_path_result.append(weight)
    
    def get_random_source_sink(self):
        s = 0
        t = s
        while t == s:
            t = random.randint(0, len(self.topology.graph)-1)
        return s, t
    
    def simulate(self):
        start_time = time.time()
        
        # pick source and sink here
        s, t = self.get_random_source_sink()
        
        with Bar("Running " + str(self.num_sims) + " simulations on a " + self.graph_name, max=self.num_sims) as bar:
            for i in range(self.num_sims):
                if self.randomize_num_nodes:
                    s, t = self.get_random_source_sink()

                self.sample_link_failure()
                self.simulate_disconnected_components()
                self.simulate_max_flow(s, t)
                self.simulate_shortest_path(s, t)
                
                if self.randomize_num_nodes:
                    self.topology = self.generate_topology()
                    self.original_graphs.append(copy.deepcopy(self.topology.graph))
                else:
                    self.topology.graph = copy.deepcopy(self.original_graphs[0]) # use deep copy to avoid copying by reference
            
                bar.next()
                  
        print("*** Total Runtime: " + str(round(time.time()-start_time, 2)) + "s")
        print("")

    def visualize_disconnected_components(self):
        graph_title = "Disconnected Components After Sampling Link Failure in a " + self.graph_name
        
        if self.randomize_num_nodes:
            disconnected_components = [result[0] for result in self.disconnected_components_result]
            total_nodes = [result[1] for result in self.disconnected_components_result]

            fig = go.Figure(data=[go.Mesh3d(x=total_nodes,
                            y=self.link_failure_samples,
                            z=disconnected_components,
                            opacity=0.5,
                            color='rgba(12,51,131,0.6)'
                            )])            
                  
            fig.write_html(os.path.join(RESULTS_DIR["disconnected_components"], self.graph_name + "__Disconnected_Components_3D_Surfaceplot.html"))

        else:
            # Making the scatter plot
            fig = px.scatter(x=self.link_failure_samples, 
                            y=self.disconnected_components_result,
                            labels=dict(x="Link Failure Rate", y="# of Disconnected Components"),
                            title=graph_title)
            
            fig.write_html(os.path.join(RESULTS_DIR["disconnected_components"], self.graph_name + "_Disconnected_Components_Scatterplot.html"))
            
            # Making the heat map
            grouping_factor = 2
            num_bins_x = 100 // grouping_factor
            num_bins_y = max(self.disconnected_components_result) // grouping_factor
            color_scale = [ 'rgb(225,231,242)', 'rgb(12,51,131)']
            
            fig = px.density_heatmap(x=self.link_failure_samples, 
                                    y=self.disconnected_components_result, 
                                    nbinsx=num_bins_x, 
                                    nbinsy=num_bins_y,
                                    labels=dict(x="Link Failure Rate", y="# of Disconnected Components"),
                                    title=graph_title)
        
            fig.write_html(os.path.join(RESULTS_DIR["disconnected_components"], self.graph_name + "_Disconnected_Components_Heatmap.html"))

    def visualize_max_flow(self):
        graph_title = "The maximum flow in a " + self.graph_name

        if self.randomize_num_nodes:
            flows = [max_flow_res[0] for max_flow_res in self.max_flow_result]
            total_nodes = [max_flow_res[1] for max_flow_res in self.max_flow_result]

            fig = go.Figure(data=[go.Mesh3d(x=total_nodes,
                            y=self.link_failure_samples,
                            z=flows,
                            opacity=0.5,
                            color='rgba(12,51,131,0.6)'
                            )])
            fig.update_layout(scene = dict(
                              xaxis_title='Number of Nodes',
                              yaxis_title='Link Failure Rate',
                              zaxis_title='Maximum Flow'))
            fig.write_html(os.path.join(RESULTS_DIR["max_flow"], self.graph_name + "_rand_nodes_max_flow.html"))  
        else:
            fig = px.scatter(x=self.link_failure_samples, 
                             y=self.max_flow_result, 
                             title=graph_title, 
                             labels={
                                  "x": "Link Failure Rate",
                                  "y": "Maximum Flow"
                            })
            fig.write_html(os.path.join(RESULTS_DIR["max_flow"], self.graph_name + "_max_flow.html"))
    
    
    def visualize_shortest_path(self):
        if self.randomize_num_nodes:
            sp_weights = [sp_result[0] for sp_result in self.shortest_path_result]
            num_nodes = [sp_result [1] for sp_result in self.shortest_path_result]

            fig = go.Figure(data=[go.Mesh3d(x=num_nodes, 
                            y=self.link_failure_samples, 
                            z=sp_weights, 
                            opacity=0.5)])
            fig.update_layout(scene = dict(
                              xaxis_title='Number of Nodes',
                              yaxis_title='Link Failure Rate',
                              zaxis_title='Weight of Shortest Path'))
            fig.write_html(os.path.join(RESULTS_DIR["shortest_path"], self.graph_name + "_SP_3D_Surfaceplot.html"))
        else:
            fig = px.scatter(x=self.link_failure_samples, y=self.shortest_path_result, title=self.graph_name + " - Link Failure Rate VS Shortest Path Weight")
            fig.update_layout(xaxis_title="Link Failure Rate", yaxis_title="Weight of Shortest path")
            # fig = px.density_heatmap(x=self.link_failure_samples,
            #                          y=self.shortest_path_result, title=self.graph_name + " - Link Failure Rate VS Shortest Path Length",
            #                          labels={
            #                              "x": "Link Failure Rate",
            #                              "y": "Length of Shortest path"
            #                          })
            fig.write_html(os.path.join(RESULTS_DIR["shortest_path"], self.graph_name + "_SP.html") )
    
    def visualize_simulation(self):
        self.visualize_disconnected_components()
        self.visualize_max_flow()
        self.visualize_shortest_path()

class FullyConnectedTopologySimulation(Simulation):
    """
    A child class of Simulation to simulate Fully Connected Topologies
    
    If num_nodes equals -1, it will randomize the topology in each individual simulation.
    Otherwise, it creates a topology from the given num_nodes and uses that for every simulation.
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
    Otherwise, it creates a topology from the given num_nodes and links_per_node and uses that for every simulation.
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
    Otherwise, it creates a topology from the given num_nodes and num_clusters and uses that for every simulation.
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

NUM_SIMS = 500
NUM_NODES = -1
NUM_CLUSTERS = 10
NUM_LINKS_PER_NODE = 10

FullyConnectedTopologySimulation = FullyConnectedTopologySimulation(NUM_SIMS, NUM_NODES)
FullyConnectedTopologySimulation.simulate()
FullyConnectedTopologySimulation.visualize_simulation()

ConstantTopologySimulation = ConstantTopologySimulation(NUM_SIMS, NUM_NODES, NUM_LINKS_PER_NODE)
ConstantTopologySimulation.simulate()
ConstantTopologySimulation.visualize_simulation()

ClusteredTopologySimulation = ClusteredTopologySimulation(NUM_SIMS, NUM_NODES, NUM_CLUSTERS)
ClusteredTopologySimulation.simulate()
ClusteredTopologySimulation.visualize_simulation()