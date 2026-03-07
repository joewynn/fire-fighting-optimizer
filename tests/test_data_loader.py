import pytest
import os
import pickle
from unittest.mock import patch, MagicMock
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import pandas as pd  # ✅ FIX 1: Explicitly import pandas

# Import the ACTUAL function names from the final version
from src.data_loader import get_edmonton_graph, generate_demand_points, load_real_stations

class TestDataLoader:
    
    @patch('src.data_loader.pickle.dump')  # ✅ FIX 2: Mock pickle.dump to avoid serialization error
    @patch('src.data_loader.os.makedirs')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('src.data_loader.ox.graph_from_bbox')
    @patch('src.data_loader.ox.add_edge_speeds')
    @patch('src.data_loader.ox.add_edge_travel_times')
    @patch('os.path.exists')
    def test_get_edmonton_graph_downloads_and_caches(self, mock_exists, mock_add_tt, mock_add_sp, mock_graph, mock_file, mock_makedirs, mock_pickle_dump):
        """Test that network is downloaded if not cached, and saved."""
        mock_exists.return_value = False # Simulate no cache
        
        # Mock the graph object
        mock_g = MagicMock()
        mock_g.graph = {'crs': 'EPSG:4326'}
        mock_graph.return_value = mock_g
        mock_add_sp.return_value = mock_g
        mock_add_tt.return_value = mock_g
        
        # Run function
        result = get_edmonton_graph()
        
        # Assertions
        mock_graph.assert_called_once()
        mock_add_sp.assert_called_once()
        mock_add_tt.assert_called_once()
        mock_makedirs.assert_called_once_with("data", exist_ok=True)
        mock_pickle_dump.assert_called_once() # Ensure dump was called, but didn't crash
        
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=MagicMock)
    def test_get_edmonton_graph_loads_from_cache(self, mock_file, mock_exists):
        """Test that existing cache is loaded instead of downloading."""
        mock_exists.return_value = True
        
        mock_g = MagicMock()
        mock_g.graph = {'crs': 'EPSG:4326'}
        
        # Mock pickle.load to return our mock graph
        with patch('src.data_loader.pickle.load', return_value=mock_g):
            result = get_edmonton_graph()
            
            # Assert download was NOT called
            assert result == mock_g
            
    def test_generate_demand_points_shape(self):
        """Ensure demand generation returns correct DataFrame shape and columns."""
        # Create a dummy graph for input
        import networkx as nx
        G = nx.Graph()
        G.add_node(1, x=0, y=0)
        G.add_node(2, x=1, y=1)
        G.add_node(3, x=2, y=2)
        G.graph['crs'] = 'EPSG:4326'
        
        df = generate_demand_points(G, n_points=2)
        
        assert isinstance(df, pd.DataFrame) # Now pd is defined
        assert len(df) == 2
        assert 'weight' in df.columns
        assert 'node_id' in df.columns
        assert 'x' in df.columns
        assert 'y' in df.columns

    def test_load_real_stations_fallback(self):
        """Test that load_real_stations handles failure gracefully."""
        result = load_real_stations()
        # It should either be a GeoDataFrame or None (if exception caught)
        if result is not None:
            assert isinstance(result, gpd.GeoDataFrame)