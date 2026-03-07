import osmnx as ox
import geopandas as gpd
import pandas as pd
import os
import pickle
import numpy as np  # ✅ FIXED: Added missing import
from shapely.geometry import Point

ox.settings.use_cache = True
ox.settings.log_console = False

def get_edmonton_graph():
    """Downloads and caches the Edmonton road network."""
    cache_path = "data/edmonton_graph.pkl"
   
    # Check cache first
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'rb') as f:
                G = pickle.load(f)
                # Verify graph has edges before returning cached version
                if len(G.edges) > 0:
                    return G
                else:
                    print("Cached graph is empty. Re-downloading...")
                    os.remove(cache_path)
        except Exception:
            print("Cache corrupted. Re-downloading...")
            if os.path.exists(cache_path): os.remove(cache_path)
    print("Downloading Edmonton road network (this may take a minute)...")
   
    try:
        # ✅ ROBUST METHOD: Use Place Name instead of BBox
        # This automatically handles the correct bounding box internally
        G = ox.graph_from_place("Edmonton, Alberta, Canada", network_type='drive', simplify=True)
       
        # Add speed and travel time attributes
        G = ox.add_edge_speeds(G)
        G = ox.add_edge_travel_times(G)
       
        # Final safety check
        if len(G.edges) == 0:
            raise ValueError("Downloaded graph has no edges. Check network_type or place name.")
        print(f"Success! Downloaded {len(G.nodes)} nodes and {len(G.edges)} edges.")
       
        os.makedirs("data", exist_ok=True)
        with open(cache_path, 'wb') as f:
            pickle.dump(G, f)
           
        return G
       
    except Exception as e:
        print(f"Error downloading graph: {e}")
        raise e

def load_real_stations():
    """Loads actual EFRS station locations from Edmonton Open Data."""
    try:
        url = "https://data.edmonton.ca/api/views/b4y7-zhnz/rows.csv?accessType=DOWNLOAD"
        df = pd.read_csv(url)
        # Basic cleanup
        df = df.dropna(subset=['Longitude', 'Latitude'])
        gdf = gpd.GeoDataFrame(
            df, 
            geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']), 
            crs="EPSG:4326"
        )
        return gdf
    except Exception as e:
        print(f"Failed to load real stations: {e}. Using synthetic fallback.")
        return None

def generate_demand_points(G, n_points=200):
    """Generates weighted demand points based on node density."""
    nodes = list(G.nodes)
    # Simple random sampling for demo; in prod, use population raster
    selected_nodes = np.random.choice(nodes, size=min(n_points, len(nodes)), replace=False)
    
    data = []
    for node in selected_nodes:
        x, y = G.nodes[node]['x'], G.nodes[node]['y']
        # Assign higher risk to industrial zones (simulated by random weight for now)
        weight = np.random.uniform(0.5, 1.0) 
        data.append({'node_id': node, 'x': x, 'y': y, 'weight': weight})
    
    return pd.DataFrame(data)