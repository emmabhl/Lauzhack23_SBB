import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import api_requests as api
import os
import api_requests as api

def string_to_actual_time(result):
    hours_nb = 0
    minutes_nb = 0
    # Get number of hours
    hours_pos = result.find("H")
    if hours_pos >= 0:
        hours_nb = int(result[2:hours_pos])
    # Get number of minutes
    minutes_pos = result.find("M")
    if minutes_pos >= 0:
        if hours_pos >= 0:
            minutes_nb = int(result[hours_pos+1:minutes_pos])
        else:
            minutes_nb = int(result[2:minutes_pos])
    # Get total time in minutes
    return hours_nb*60 + minutes_nb

#Plus utile depuis que get_trips_infos existe
def trip_durations(trips):
    return [string_to_actual_time(trip["duration"]) for trip in trips]

def get_train_stations(places):
    return [place for place in places["places"] if "Train" in [mode["name"] for mode in place["vehicleModes"]]]

def get_closest_train_station(nearby_places):
    """
    This function returns the closes train station from the list of nearby places, if any.
    """
    for place in nearby_places["places"]:
        if "Train" in [mode["name"] for mode in place["vehicleModes"]]:
            return place
    return None

def is_applicable(position, waiting_time_threshold):
    """
    This function is used to check if a position is applicable for the new implementation or not. 
    It first looks at how many public transport stops are in a 1km radius around it, corrresponding to an 
    about 10 minute walk, and returns False if public transport is very accessible.
    It doesn't concretely look at the actual number of stops, but rather computes an "average waiting time"
    the person would have to wait for public transport, and returns False if this waiting time is lower than
    the given threshold.

    This function also looks at the distance to the smallest train station. If this distance itself is less than 1km
    which again corresponds to a 10min walk, then the function returns False.
    """

    # Get the nearby public transport places in a 1km radius
    nearby_places = api.get_nearby_places(longitude=position[0], latitude=position[1], radius=1000, type="StopPlace", limit=50, includeVehicleModes=False)
    # For each place get the number of vehicle journeys
    number_journeys = [len(api.get_place_from_id(place["id"])["departures"]) for place in nearby_places["places"] if "departures" in api.get_place_from_id(place["id"]).keys()]
    # Compute the average waiting time (assuming each public transport comes every 30mins on average)
    average_waiting_time = 99999
    if np.sum(number_journeys) > 0:
        average_waiting_time = 60/(np.sum(number_journeys)/2) # in minutes, divide total number of journeys by 2 to account for 2-way traffic
    # Compute distance to closest trainstation
    train_station = get_closest_train_station(nearby_places)
    # Return applicability
    # Applicable only if the waiting time is too big and there is no train station in close proximity
    return average_waiting_time > waiting_time_threshold and train_station is None
def departure_to_time(trip):
    """Returns the departure time of a trip"""
    departure = trip['legs'][0]['serviceJourney']['stopPoints'][0]['departure']['timeAimed']
    departure = datetime.strptime(departure, '%Y-%m-%dT%H:%M:%S%z')
    departure = departure.replace(tzinfo=None)
    return departure

#Plus utile depuis que get_trips_infos existe
def get_departures_times(trips):
    return [departure_to_time(trip) for trip in trips]

def get_trips_infos(journey):
    res = []
    for trip in journey['trips']:
        numberStops = 0
        for leg in trip['legs']:
            for stop_point in leg['serviceJourney']['stopPoints']:
                if stop_point['place']['type'] == 'StopPlace':
                    numberStops += 1 
        
        departure_time = departure_to_time(trip)
        duration = string_to_actual_time(trip['duration'])
        
        res.append({'id' : trip['id'], 'departune_time':departure_time, 'duration':duration,  'numberLegs' : len(trip['legs']), 'TotNumberStops': numberStops })
    return res

def get_stations(location_name):
    """Extracts all stations associated with a location name
    Args:
        location_name (string): Name of the location (e.g. City)
    Returns:
        list: List of stations associated with the location name
    """
    all_locations = pd.DataFrame(api.get_places(location_name)['places'])[['id', 'name', 'type', 'canton', 'centroid']]
    # only keep the coordinates of the centroid
    all_locations['centroid'] = all_locations['centroid'].apply(lambda x: x['coordinates'])
    return all_locations[all_locations['type'] == 'StopPlace']

def get_station_id(station):
    return station["id"]
