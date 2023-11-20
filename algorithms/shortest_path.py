def shortest_paths(G, source):
    explored_nodes = []
    new_graph = [[0 for _ in range(len(G))] for _ in range(len(G))]
    distance = [float('inf')] * len(G)
    distance[source] = 0
    predecessor = [None] * len(G)

    while len(explored_nodes) < len(G):
        min_distance = float('inf')
        min_node = None

        # find node with minimum distance from source
        for node in range(len(G)):
            if node not in explored_nodes and distance[node] < min_distance:
                min_distance = distance[node]
                min_node = node
        explored_nodes.append(min_node)
        if min_node != source:
            new_graph[predecessor[min_node]][min_node] = 1
            new_graph[min_node][predecessor[min_node]] = 1

        for node in range(len(G)):
            if node not in explored_nodes and G[min_node][node] != 0:
                if distance[min_node] + G[min_node][node] < distance[node]:
                    distance[node] = distance[min_node] + G[min_node][node]
                    predecessor[node] = min_node
    
    return new_graph