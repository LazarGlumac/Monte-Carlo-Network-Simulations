import heapq

def shortest_paths(G, source, dest=None):
    explored_nodes = []
    new_graph = [[0 for _ in range(len(G))] for _ in range(len(G))]
    distance = MinHeap()
    predecessor = [None] * len(G)

    for i in range(len(G)):
        if i == source:
            distance.add_node(i, 0)
        else:
            distance.add_node(i, float('inf'))

    while len(explored_nodes) < len(G):
        min_d_node = distance.pop_node()
        explored_nodes.append(min_d_node[1])
        
        if min_d_node[1] != source:
            new_graph[predecessor[min_d_node[1]]][min_d_node[1]] = 1
            new_graph[min_d_node[1]][predecessor[min_d_node[1]]] = 1
        
        for node in range(len(G)):
            if node not in explored_nodes and G[min_d_node[1]][node] != 0:
                if min_d_node[0] + G[min_d_node[1]][node] < distance.entry_finder[node][0]:
                    distance.add_node(node, min_d_node[0] + G[min_d_node[1]][node])
                    predecessor[node] = min_d_node[1]
    
    return new_graph


class MinHeap():
    heap = []
    entry_finder = {}
    REMOVED = -1

    def add_node(self, node, priority=0):
        if node in self.entry_finder:
            self.remove_node(node)
        entry = [priority, node]
        self.entry_finder[node] = entry
        heapq.heappush(self.heap, entry)

    def remove_node(self, node):
        entry = self.entry_finder.pop(node)
        entry[-1] = self.REMOVED

    def pop_node(self):
        while self.heap:
            priority, node = heapq.heappop(self.heap)
            if node is not self.REMOVED:
                del self.entry_finder[node]
                return [priority, node]
        raise KeyError('pop from an empty priority queue')