import pytest
import networkx as nx
import pandas as pd

@pytest.fixture
def sample_graph():
    """Creates a small deterministic graph for testing."""
    G = nx.Graph()
    # Nodes 0-4 in a line, 100m apart
    for i in range(5):
        G.add_node(i, x=i*100, y=0)
        if i > 0:
            G.add_edge(i-1, i, length=100, travel_time=10) # 10s per edge
    G.graph['crs'] = 'EPSG:4326'
    return G

@pytest.fixture
def sample_demands(sample_graph):
    """Demands at nodes 0, 2, 4. Matches the NEW DataFrame structure."""
    df = pd.DataFrame({
        'node_id': [0, 2, 4],
        'x': [0, 200, 400],
        'y': [0, 0, 0],
        'weight': [1.0, 0.5, 0.2]
    })
    return df

@pytest.fixture
def sample_candidates(sample_graph):
    """Candidates at nodes 1 and 3."""
    return [1, 3]