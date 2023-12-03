from pyrosm import OSM, get_data
import geopandas as gpd
import pandas as pd
from sklearn.neighbors import BallTree
import numpy as np
import mapclassify as mc
import matplotlib.pyplot as plt
import time
import networkx as nx
import igraph as ig
import osmnx as ox
import folium
import json
import os

def download_map(area = "Switzerland"):
    
    return OSM(get_data(area, directory=os.getcwd()), bounding_box = 

def compute_routes_and_times(city, route_type = ['driving', 'walking', 'driving+service']): #, 'cycling']):
    osm = get_map(city)
    graph = {}
    for route in route_type:
        extra_kwargs = {"hv":{"car":120}} if route == 'driving' else {}
        n, e = osm.get_network(nodes=True, network_type=route)
        graph[route] = ox.add_edge_travel_times(ox.add_edge_speeds(osm.to_graph(n, e, graph_type="networkx")), extra_kwargs=extra_kwargs)
    return graph

def get_route(source_geo, dest_geo, go_type='drive', weight='travel_time',plot=False):
    graph_type = compute_routes_and_times('Amsterdam')
    source_node = ox.get_nearest_node(graph_type[go_type], source_geo)
    target_node = ox.get_nearest_node(graph_type[go_type], dest_geo)

    route = nx.shortest_path(graph_type[go_type], source_node, target_node, weight=weight)
    
    edge_lengths = ox.utils_graph.get_route_edge_attributes(graph_type[go_type], route, 'length') 
    edge_travel_time = ox.utils_graph.get_route_edge_attributes( graph_type[go_type], route, 'travel_time') 
    total_route_length = round(sum(edge_lengths), 1)
    route_travel_time  = round(sum(edge_travel_time)/60, 2)
    if plot:
      ox.plot_graph_route(graph_type[go_type], route, node_size=0, figsize=(40,40))
    return route, total_route_length, route_travel_time
