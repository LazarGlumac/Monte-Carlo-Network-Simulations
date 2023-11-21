def find_num_components(G):
    visited = [False for i in range(len(G))]
    num_components = 0
    
    def dfs(current_node):
        visited[current_node] = True
    
        for i in range(len(G)):
            if G[current_node][i] > 0 and (not visited[i]):
                dfs(i)
    
    while False in visited:
        num_components += 1
        next_node = visited.index(False)
        dfs(next_node)
    
    return num_components