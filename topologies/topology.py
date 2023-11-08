import random
import networkx as nx 
import matplotlib.pyplot as plt 
import heapq 

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

    def visualize(self) -> str:
        G = nx.DiGraph()
        for i in range(len(self.graph)): 
            for j in range(len(self.graph[i])): 
                if self.graph[i][j] == 1 and i != j: # Ignore self loops in visualization
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
        self.graph = [[1 for _ in range(n)] for _ in range(n)]


class ConstantTopology(Topology):
    """
    A class to represent a topology of a network where each node has a constant
    number of links. 
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
            num_links = sum(self.graph[i]) - 1
            available.remove(i)

            push_back = [] # Store the nodes that were popped from the heap but not used
            while num_links < links_per_node:
                candidate = heapq.heappop(link_heap) # Pop the node with the fewest links
                if candidate[1] not in available:
                    continue
                if self.graph[i][candidate[1]] == 0:
                    self.graph[i][candidate[1]] = 1
                    self.graph[candidate[1]][i] = 1
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
            self.graph[centroid][(centroid + cluster_size) % n] = 1
            self.graph[(centroid + cluster_size) % n][centroid] = 1
            # TODO should there be random cross links between the centroid ring?
            for child in range(cluster_size): # Make an edge between the centroid and each child
                self.graph[centroid][centroid + child] = 1
                self.graph[centroid + child][centroid] = 1
            links_in_cluster = random.randint(0, cluster_size*(cluster_size-1)//2) # Randomly interconnect nodes in cluster
            # TODO should this be a random number of links or a constant number of links?
            while links_in_cluster > 0:
                linked_nodes = random.sample(range(cluster_size), 2)
                if linked_nodes[0] != centroid and linked_nodes[1] != centroid:
                    self.graph[centroid + linked_nodes[0]][centroid + linked_nodes[1]] = 1
                    self.graph[centroid + linked_nodes[1]][centroid + linked_nodes[0]] = 1
                    links_in_cluster -= 1
