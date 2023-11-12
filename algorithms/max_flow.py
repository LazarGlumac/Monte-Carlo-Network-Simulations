import random

def max_flow(G):
    n = len(G)
    sink = random.randint(0, n-1)
    source = random.choice([x for x in range(n) if x != sink])

    modified_graph = [[0 for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                modified_graph[i][j] = G[i][j]

    for i in range(n):
        modified_graph[i][source] = 0
        modified_graph[sink][i] = 0

    modified_graph[source][sink] = 0
    modified_graph[sink][source] = 0

    max_flow =  ford_fulkerson(modified_graph, source, sink)
    flow_generated = 0
    for u, _ in max_flow:
        if u == source:
            flow_generated += max_flow[(u, _)]
    return flow_generated

def consruct_residual(G, flow):
    pass

def augment(flow, path):
    pass

def ford_fulkerson(G, s, t, capacities):
    n = len(G)
    flow = {}
    # Initialize all flows to 0
    for i in range(n):
        for j in range(n):
            if G[i][j] != 1:
                flow[(i, j)] = 0
    residual_graph = consruct_residual()
    while path := dfs(residual_graph, s, t):
        pass

    pass

def dfs(G, s, t):
    pass