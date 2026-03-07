import folium

def create_optimization_map(G, candidates, selected_indices, demands, travel_matrix, show_baseline=False, baseline_stations=None):
    """Generates an interactive Folium map with optional baseline."""
    # Center on Edmonton
    m = folium.Map(location=[53.5461, -113.4938], zoom_start=11, tiles='CartoDB dark_matter')
    
    # Plot Demand Points (Heatmap style)
    for _, row in demands.iterrows():
        folium.CircleMarker(
            location=[row['y'], row['x']],
            radius=3,
            color='#FFFF00',
            fill=True,
            fill_opacity=0.4,
            weight=0
        ).add_to(m)
    
    # Plot Optimized Candidates (Red)
    for i, node in enumerate(candidates):
        if i in selected_indices:
            x, y = G.nodes[node]['x'], G.nodes[node]['y']
            folium.CircleMarker(
                location=[y, x],
                radius=8,
                color='red',
                fill=True,
                fill_opacity=1.0,
                popup="Optimized New Station"
            ).add_to(m)
            
            # Draw simple 4-min coverage circle for selected stations
            folium.Circle(
                location=[y, x],
                radius=3500, # Approx 4km for 4 mins
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.15
            ).add_to(m)
    
    # ✅ NEW: Plot Baseline Current Stations (Blue)
    if show_baseline and baseline_stations is not None:
        for _, row in baseline_stations.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=6,
                color='blue',
                fill=True,
                fill_opacity=0.7,
                popup="Current Existing Station"
            ).add_to(m)
            
    folium.LayerControl().add_to(m)
    return m