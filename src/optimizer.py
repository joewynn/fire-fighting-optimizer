import pulp
import numpy as np
import pandas as pd

def solve_mclp(candidates, demands, travel_matrix, p_stations, time_threshold=240):
    """
    Stage 1: Maximal Covering Location Problem (MILP)
    Maximizes weighted demand covered within time_threshold using p_stations.
    """
    prob = pulp.LpProblem("Fire_MCLP", pulp.LpMaximize)
    
    # Decision Variables
    x = {j: pulp.LpVariable(f"x_{j}", cat='Binary') for j in range(len(candidates))}
    y = {i: pulp.LpVariable(f"y_{i}", cat='Binary') for i in range(len(demands))}
    
    # Objective: Maximize Weighted Coverage
    prob += pulp.lpSum([demands.iloc[i]['weight'] * y[i] for i in range(len(demands))])
    
    # Constraint 1: Coverage Logic
    for i in range(len(demands)):
        covering_candidates = [
            j for j in range(len(candidates)) 
            if travel_matrix[i][j] <= time_threshold
        ]
        if covering_candidates:
            prob += pulp.lpSum([x[j] for j in covering_candidates]) >= y[i]
        else:
            prob += y[i] == 0  # Impossible to cover
            
    # Constraint 2: Number of Stations
    prob += pulp.lpSum([x[j] for j in range(len(candidates))]) == p_stations
    
    # Solve
    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=60)
    prob.solve(solver)
    
    if pulp.LpStatus[prob.status] != 'Optimal':
        raise RuntimeError("Optimization failed to find optimal solution.")
        
    selected_indices = [j for j in range(len(candidates)) if x[j].value() > 0.5]
    objective_value = pulp.value(prob.objective)
    
    return selected_indices, objective_value

def run_monte_carlo_stress_test(selected_indices, candidates, demands, travel_matrix, n_simulations=500, busy_prob=0.3):
    """
    Stage 2: Metaheuristic Stress Test
    Simulates unit unavailability to calculate PoA and 90th Percentile Response Time.
    """
    response_times = []
    coverage_ratios = []
    
    # ✅ FIXED: Removed unused 'candidate_nodes' line
    
    for _ in range(n_simulations):
        # Simulate Availability
        available_indices = [
            i for i in selected_indices 
            if np.random.rand() > busy_prob
        ]
        
        if not available_indices:
            response_times.append(9999)
            coverage_ratios.append(0)
            continue
            
        sim_times = []
        covered_weight = 0
        total_weight = demands['weight'].sum()
        
        for i, row in demands.iterrows():
            min_time = 9999
            for j in available_indices:
                t = travel_matrix[i][j]
                if t < min_time:
                    min_time = t
            
            sim_times.append(min_time)
            if min_time <= 240: # 4 mins
                covered_weight += row['weight']
        
        # Calculate Metrics for this simulation
        sim_times.sort()
        p90_idx = int(len(sim_times) * 0.9)
        response_times.append(sim_times[p90_idx] if p90_idx < len(sim_times) else 9999)
        coverage_ratios.append(covered_weight / total_weight)
    
    return {
        'p90_response_time': np.percentile(response_times, 100), # Worst case of the P90s
        'avg_p90': np.mean(response_times),
        'avg_coverage': np.mean(coverage_ratios),
        'min_coverage': np.min(coverage_ratios)
    }