import pytest
from src.optimizer import solve_mclp, run_monte_carlo_stress_test
from src.geospatial import compute_travel_matrix
import numpy as np

def test_mclp_selects_best_coverage(sample_graph, sample_demands, sample_candidates):
    """Verify MCLP picks the candidate covering the highest weight."""
    travel_matrix = compute_travel_matrix(sample_graph, sample_candidates, sample_demands)
    # Threshold 25s: 
    # Cand 1 (Node 1) covers Demand 0 (10s), Demand 2 (10s). Total Weight = 1.5
    # Cand 3 (Node 3) covers Demand 2 (10s), Demand 4 (10s). Total Weight = 0.7
    # With p=1, it MUST pick Candidate 1 (Index 0)
    
    selected, obj = solve_mclp(sample_candidates, sample_demands, travel_matrix, p_stations=1, time_threshold=25)
    
    assert len(selected) == 1
    assert selected[0] == 0 # Index of Candidate 1
    assert obj == 1.5

def test_stress_test_returns_valid_metrics(sample_graph, sample_demands, sample_candidates):
    """Ensure stress test returns expected dictionary structure."""
    travel_matrix = compute_travel_matrix(sample_graph, sample_candidates, sample_demands)
    selected = [0, 1] # Use both
    
    metrics = run_monte_carlo_stress_test(
        selected, sample_candidates, sample_demands, travel_matrix, 
        n_simulations=10, busy_prob=0.5
    )
    
    assert 'avg_p90' in metrics
    assert 'avg_coverage' in metrics
    assert 0 <= metrics['avg_coverage'] <= 1
    assert metrics['avg_p90'] >= 0