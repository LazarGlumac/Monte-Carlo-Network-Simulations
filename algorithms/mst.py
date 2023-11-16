import random

def MST(G):
    INF = 99999999
    
    vertices = len(G)
    mst_edges = []
    
    selected = [False for i in range(vertices)]
    num_edges = 0
    
    selected[0] = True
    while (num_edges < vertices - 1):
        min = INF
        x = 0
        y = 0
        for i in range(vertices):
            if selected[i]:
                for j in range(vertices):
                    if i != j and (not selected[j]) and G[i][j] > 0:
                        if min > G[i][j]:
                            min = G[i][j]
                            x = i
                            y = j
        mst_edges.append((x,y))
        selected[y] = True 
        num_edges += 1
        
    return mst_edges