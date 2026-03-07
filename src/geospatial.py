import networkx as nx
import numpy as np

def compute_travel_matrix(G, candidates, demands):
    """
    Computes a matrix (len(demands) x len(candidates)) of travel times in seconds.
    Uses Dijkstra for each candidate.
    """
    n_demands = len(demands)
    n_cands = len(candidates)
    matrix = np.full((n_demands, n_cands), 9999.0)
    
    # Map demand dataframe index to graph node ID
    # Note: demands has 'node_id' column from data_loader
    demand_node_ids = demands['node_id'].tolist()
    
    for j, cand_node in enumerate(candidates):
        # Single source shortest path from candidate to all nodes
        lengths = nx.single_source_dijkstra_path_length(G, cand_node, weight='travel_time')
        
        for i, d_node in enumerate(demand_node_ids):
            if d_node in lengths:
                matrix[i][j] = lengths[d_node]
            # Else remains 9999 (unreachable)
            
    return matrix