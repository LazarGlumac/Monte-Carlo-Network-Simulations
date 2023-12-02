import random
import networkx as nx 
import matplotlib.pyplot as plt 
import heapq 

MAX_EDGE_WEIGHT = 10

class Topology():
    """
    A class to represent a topology of a network
    """
    graph = None
    def __init__(self, n) -> None:
        if n < 1:
            raise Exception("Number of nodes must be greater than 0")
        self.graph = [[0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            self.graph[i][i] = 1
    
    def destroy_link(self, i, j):
        self.graph[i][j] = 0
        self.graph[j][i] = 0

    def get_random_edge_weight(self):
        return random.randint(1, MAX_EDGE_WEIGHT)

    def visualize(self):
        G = nx.DiGraph()
        for i in range(len(self.graph)): 
            for j in range(len(self.graph[i])): 
                if self.graph[i][j] > 0 and i != j: # Ignore self loops in visualization
                    G.add_edge(i,j)  

        nx.draw(G, with_labels=True) 
        plt.show()

class FullyConnectedTopology(Topology):
    """
    A class to represent a fully connected topology of a network. 
    ie, all pairs of nodes are connected)
    """
    def __init__(self, n) -> None:
        super().__init__(n)
        for i in range(n):
            for j in range(i):
                self.graph[i][j] = self.get_random_edge_weight()
                self.graph[j][i] = self.graph[i][j]


class ConstantTopology(Topology):
    """
    A class to represent a topology of a network where each node has a 
    maximum constant number of links. 
    """
    def __init__(self, n, links_per_node) -> None:
        if links_per_node > n-1:
            raise Exception("Too many links for this topology")
        elif links_per_node < 1:
            raise Exception("Too few links for this topology")

        super().__init__(n)

        available = list(range(n))
        link_heap = [(0, i) for i in available] # Heap to sort nodes by number of links
        heapq.heapify(link_heap)

        for i in range(n):
            if i not in available:
                continue
            num_links = sum([1 for edge_weight in self.graph[i] if edge_weight > 0]) - 1
            available.remove(i)

            push_back = [] # Store the nodes that were popped from the heap but not used
            while num_links < links_per_node and link_heap:
                candidate = heapq.heappop(link_heap) # Pop the node with the fewest links
                if candidate[1] not in available:
                    continue
                if self.graph[i][candidate[1]] == 0:
                    edge_weight = self.get_random_edge_weight()
                    self.graph[i][candidate[1]] = edge_weight
                    self.graph[candidate[1]][i] = edge_weight
                    if candidate[0] + 1 < links_per_node: # If the node has less than the max number of links, push it back onto the heap
                        heapq.heappush(link_heap, (candidate[0] + 1, candidate[1]))
                    else: # Otherwise, remove it from the list of available nodes and dont push it back on the heap
                        available.remove(candidate[1])
                    num_links += 1
                else: # There already exists an edge between the two nodes
                    push_back.append(candidate)
            for item in push_back:
                heapq.heappush(link_heap, item)
                

class ClusteredTopology(Topology):
    """
    A class to represent a topology of a network where nodes are clustered. The
    nodes within a given cluster are all connected to the centroid of the cluster.
    The centroids of each cluster are connected in a ring.
    """
    def __init__(self, n, num_clusters) -> None:
        if num_clusters > n:
            raise Exception("Too many clusters for this topology")
        elif n % num_clusters != 0:
            raise Exception("Number of nodes must be divisible by number of clusters")

        super().__init__(n)
        
        cluster_size = n // num_clusters
        for centroid in range(0, n, cluster_size):
            # Make an edge between the centroid and the next centroid in the ring
            edge_weight = self.get_random_edge_weight()
            self.graph[centroid][(centroid + cluster_size) % n] = edge_weight
            self.graph[(centroid + cluster_size) % n][centroid] = edge_weight
            for child in range(cluster_size): # Make an edge between the centroid and each child
                edge_weight = self.get_random_edge_weight()
                self.graph[centroid][centroid + child] = edge_weight
                self.graph[centroid + child][centroid] = edge_weight
            links_in_cluster = random.randint(0, cluster_size*(cluster_size-1)//2) # Randomly interconnect nodes in cluster
            while links_in_cluster > 0:
                linked_nodes = random.sample(range(cluster_size), 2)
                if linked_nodes[0] != centroid and linked_nodes[1] != centroid:
                    edge_weight = self.get_random_edge_weight()
                    self.graph[centroid + linked_nodes[0]][centroid + linked_nodes[1]] = edge_weight
                    self.graph[centroid + linked_nodes[1]][centroid + linked_nodes[0]] = edge_weight
                    links_in_cluster -= 1
