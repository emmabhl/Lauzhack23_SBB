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

def download_map(area):
    # Check if a directory with the name of the area exists
    if not os.path.exists(area + '_data'):
        os.makedirs(area + '_data')
        get_data(area, directory = os.getcwd() + '/' + area + '_data')

    # Get the created file
    file = [f for f in os.listdir(area + '_data') if os.path.isfile(os.path.join(area + '_data', f))]
    if len(file) == 0:
        raise Exception('No file found in the directory')
    elif len(file) > 1:
        raise Exception('More than one file found in the directory')
    else:
        return file[0] 


def get_map(bounds_coordinate, area = "Switzerland"):
    file_path = download_map(area)
    osm = OSM(file_path, bounding_box=bounds_coordinate)
    return osm


def define_map_bounds(start, destination):
    # Define the bounds of the map
    bounds = [min(start['longitude'], destination['longitude']), min(start['latitude'], destination['latitude']), max(start['longitude'], destination['longitude']), max(start['latitude'], destination['latitude'])]
    return bounds

def compute_all_travel_times():
    # Load the Swiss map by batch
    latitude_range = [45.4905, 47.4830]
    longitude_range = [5.5723, 10.2931]

    # Define the number of batches
    n_batches = 20

    # Define the size of each batch
    latitude_batch_size = (latitude_range[1] - latitude_range[0])/n_batches
    longitude_batch_size = (longitude_range[1] - longitude_range[0])/n_batches

    # Loop over the batches
    for i in range(n_batches):
        for j in range(n_batches):
            # Define the bounds of the map
            bounds = [longitude_range[0] + i*longitude_batch_size, latitude_range[0] + j*latitude_batch_size, longitude_range[0] + (i+1)*longitude_batch_size, latitude_range[0] + (j+1)*latitude_batch_size]
            osm = get_map(bounds)

            # Compute the travel times
            n, e = osm.get_network(nodes=True, network_type='driving')
            graph = ox.add_edge_travel_times(ox.add_edge_speeds(osm.to_graph(n, e, graph_type="networkx")), extra_kwargs={"hv":{"car":120}})

            # Save the graph
            if not os.path.exists("time_travel_data"):
                os.makedirs("time_travel_data")
            nx.write_gpickle(graph, "time_travel_data/graph_" + str(i) + "_" + str(j) + ".gpickle")

def combine_all_travel_times():
    # Load the saved graphs
    graphs = []
    for i in range(20):
        for j in range(20):
            graphs.append(nx.read_gpickle("time_travel_data/graph_" + str(i) + "_" + str(j) + ".gpickle"))

    # Combine the graphs
    graph = nx.compose_all(graphs)

    # Save the graph
    nx.write_gpickle(graph, "time_travel_graph.gpickle")

def get_travel_time(start, destination, weight='travel_time', plot=True):
    # Load the graph
    graph = nx.read_gpickle("time_travel_graph.gpickle")

    # Get the nodes
    source_node = ox.get_nearest_node(graph, (start['latitude'], start['longitude']))
    target_node = ox.get_nearest_node(graph, (destination['latitude'], destination['longitude']))

    # Compute the route
    route = nx.shortest_path(graph, source_node, target_node, weight=weight)

    edge_lengths = ox.utils_graph.get_route_edge_attributes(graph, route, 'length')
    edge_travel_time = ox.utils_graph.get_route_edge_attributes(graph, route, 'travel_time')
    total_route_length = round(sum(edge_lengths), 1)
    route_travel_time  = round(sum(edge_travel_time)/60, 2)
    if plot:
        ox.plot_graph_route(graph, route, node_size=0, figsize=(40,40))
    return route, total_route_length, route_travel_time

    
            
    

"""def compute_routes_and_times(city, route_type = ['driving', 'walking', 'driving+service']): #, 'cycling']):
    osm = get_map(
    graph = {}
    for route in route_type:
        extra_kwargs = {"hv":{"car":120}} if route == 'driving' else {}
        n, e = osm.get_network(nodes=True, network_type=route)
        graph[route] = ox.add_edge_travel_times(ox.add_edge_speeds(osm.to_graph(n, e, graph_type="networkx")), extra_kwargs=extra_kwargs)
    return graph"""
