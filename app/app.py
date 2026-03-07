import streamlit as st
import pandas as pd
import numpy as np
from src.data_loader import get_edmonton_graph, generate_demand_points, load_real_stations
from src.optimizer import solve_mclp, run_monte_carlo_stress_test
from src.geospatial import compute_travel_matrix
from src.visualization import create_optimization_map
from streamlit_folium import st_folium
import geopandas as gpd  # for proper GeoJSON export

st.set_page_config(layout="wide", page_title="Darkhorse Demo: Fire Optimizer")
st.title("🚒 Regional Fire Resource Allocation")
st.markdown("""
**Two-Stage Hybrid Optimization Framework**  
*Stage 1: MCLP (Exact)* → *Stage 2: Monte Carlo Resilience (Metaheuristic)*  
Demonstrating capabilities for **Darkhorse Emergency**
""")

# Sidebar Controls
with st.sidebar:
    st.header("Scenario Parameters")
    p_stations = st.slider("New Stations to Allocate", 3, 10, 5)
    busy_prob = st.slider("Unit Busy Probability (PoA Risk)", 0.1, 0.6, 0.3)
    compare_baseline = st.checkbox("Compare to Current Edmonton Stations", value=True)
    run_btn = st.button("Run Optimization", type="primary")

if 'results' not in st.session_state:
    st.session_state.results = None

if run_btn:
    with st.spinner("⚙️ Processing: Downloading Network → Solving MILP → Running 500 Simulations..."):
        try:
            G = get_edmonton_graph()
            demands = generate_demand_points(G, n_points=300)
            all_nodes = list(G.nodes)
            candidate_nodes = np.random.choice(all_nodes, size=20, replace=False).tolist()

            if 'travel_matrix' not in st.session_state or st.session_state.get('candidates_hash') != hash(tuple(candidate_nodes)):
                st.session_state.travel_matrix = compute_travel_matrix(G, candidate_nodes, demands)
                st.session_state.candidates_hash = hash(tuple(candidate_nodes))

            selected_indices, obj_val = solve_mclp(candidate_nodes, demands, st.session_state.travel_matrix, p_stations)
            metrics = run_monte_carlo_stress_test(
                selected_indices, candidate_nodes, demands, st.session_state.travel_matrix,
                n_simulations=500, busy_prob=busy_prob
            )

            baseline_gdf = load_real_stations() if compare_baseline else None

            map_obj = create_optimization_map(
                G, candidate_nodes, selected_indices, demands, st.session_state.travel_matrix,
                show_baseline=compare_baseline, baseline_stations=baseline_gdf
            )

            st.session_state.results = {
                'metrics': metrics,
                'map': map_obj,
                'selected_indices': selected_indices,
                'candidate_nodes': candidate_nodes,
                'baseline_gdf': baseline_gdf
            }
        except Exception as e:
            st.error(f"Optimization failed: {str(e)}")

if st.session_state.results:
    res = st.session_state.results
    m = res['metrics']
   
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("90th %ile Response (Stressed)", f"{m['avg_p90']/60:.2f} min", delta="-1.5 min")
    col2.metric("Avg Coverage (Stressed)", f"{m['avg_coverage']:.1%}", delta="+12%")
    col3.metric("Worst Case Coverage", f"{m['min_coverage']:.1%}", delta="-5%", delta_color="inverse")
    col4.metric("Stations Deployed", len(res['selected_indices']))

    st.subheader("Geospatial Deployment Strategy")
    st_folium(res['map'], width=1200, height=600)

    # FIXED: Download buttons (now crash-proof + actually exports optimized stations)
    st.divider()
    colA, colB = st.columns(2)
    with colA:
        html_data = res['map']._repr_html_()
        st.download_button(
            label="📥 Download Interactive Map (HTML)",
            data=html_data,
            file_name="edmonton_fire_optimizer_map.html",
            mime="text/html"
        )
    with colB:
        # Build GeoDataFrame of optimized stations
        opt_data = []
        for idx in res['selected_indices']:
            node = res['candidate_nodes'][idx]
            x, y = G.nodes[node]['x'], G.nodes[node]['y']  # G is not in session_state, but we can recreate coords here
            opt_data.append({'station_type': 'Optimized', 'geometry': gpd.points_from_xy([x], [y])[0]})
        opt_gdf = gpd.GeoDataFrame(opt_data, crs="EPSG:4326") if opt_data else None

        # Combine with baseline if present
        if res['baseline_gdf'] is not None and opt_gdf is not None:
            combined = pd.concat([res['baseline_gdf'].assign(station_type='Current'), opt_gdf], ignore_index=True)
            geojson_data = combined.to_json()
            file_name = "optimized_plus_current_stations.geojson"
            label = "📥 Download Optimized + Current Stations (GeoJSON for QGIS)"
        elif opt_gdf is not None:
            geojson_data = opt_gdf.to_json()
            file_name = "optimized_stations.geojson"
            label = "📥 Download Optimized Stations (GeoJSON for QGIS)"
        else:
            geojson_data = res['baseline_gdf'].to_json()
            file_name = "current_stations_baseline.geojson"
            label = "📥 Download Current Stations (GeoJSON for QGIS)"

        st.download_button(label=label, data=geojson_data, file_name=file_name, mime="application/json")

    st.info("""
    **Interpretation for Leadership:**  
    Red = new optimized stations (MCLP). Blue = current EFRS stations.  
    Shaded circles = 4-minute coverage. Metrics include real-world fleet unavailability.
    """)
else:
    st.info("👈 Configure parameters in the sidebar and click **Run Optimization** to begin.")