import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import api_requests as api
import os
import math
import osm_helpers

LIST_TRANSPORT = ["TRAIN", "TRAMWAY", "BUS", "CABLEWAY", "SHIP", "METRO"]

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

def departure_to_time(trip, leg_nb=0):
    """Returns the departure time of a trip"""
    if np.isin(trip['legs'][leg_nb]['mode'], LIST_TRANSPORT):
        departure = trip['legs'][leg_nb]['serviceJourney']['stopPoints'][0]['departure']['timeAimed']
    elif trip['legs'][leg_nb]['mode'] == 'FOOT':
        departure = trip['legs'][leg_nb]['start']['timeAimed']
    else:
        print(trip['legs'][leg_nb]['mode'])
        
    departure = datetime.strptime(departure, '%Y-%m-%dT%H:%M:%S%z')
    departure = departure.replace(tzinfo=None)
    return departure

def arrival_to_time(trip, leg_nb=-1):
    """Returns the arrival time of a trip"""

    if np.isin(trip['legs'][leg_nb]['mode'], LIST_TRANSPORT):
        arrival = trip['legs'][leg_nb]['serviceJourney']['stopPoints'][-1]['arrival']['timeAimed']
    elif trip['legs'][leg_nb]['mode'] == 'FOOT':
        arrival = trip['legs'][leg_nb]['end']['timeAimed']
    else:
        print(trip['legs'][leg_nb])
    arrival = datetime.strptime(arrival, '%Y-%m-%dT%H:%M:%S%z')
    arrival = arrival.replace(tzinfo=None)
    return arrival

#Plus utile depuis que get_trips_infos existe
def get_departures_times(trips):
    return [departure_to_time(trip) for trip in trips]

def takes_car(origin):
    # Get the nearby public transport places in a 1km radius
    nearby_places = api.get_nearby_places(longitude=origin[0], latitude=origin[1], radius=1000, type="StopPlace", limit=50, includeVehicleModes=False)
    # Compute distance to closest trainstation
    train_station = get_closest_train_station(nearby_places)
    return train_station is None

def get_trips_infos(journey):
    res = []
    for trip in journey['trips']:
        stopPlaces = []
        legs_mode = []
        start_legs = []
        end_legs = []
        legs_start_time = []
        legs_end_time = []
        
        for i, leg in enumerate(trip['legs']):
            legs_mode.append(leg['mode'])
            legs_start_time.append(departure_to_time(trip, i))
            legs_end_time.append(arrival_to_time(trip, i))
            if np.isin(legs_mode[-1], LIST_TRANSPORT):
                start_legs.append(leg['serviceJourney']['stopPoints'][0]['place']['name'])
                end_legs.append(leg['serviceJourney']['stopPoints'][-1]['place']['name'])
                for stop_point in leg['serviceJourney']['stopPoints']:
                    if (stop_point['place']['type'] == 'StopPlace') and ((len(stopPlaces)==0) or (stop_point['place']['id'] != stopPlaces[-1])):
                        stopPlaces.append(stop_point['place']['id'])
            elif legs_mode[-1] == 'FOOT':
                start_legs.append(leg['start']['place']['name'])
                end_legs.append(leg['end']['place']['name'])
                stop_point = leg['start']['place']
                if (stop_point['type'] == 'StopPlace') and ((len(stopPlaces)==0) or (stop_point['id'] != stopPlaces[-1])):
                    stopPlaces.append(stop_point['id'])
        
        departure_time = departure_to_time(trip)
        arrival_time = arrival_to_time(trip)
        duration = string_to_actual_time(trip['duration'])
        
        res.append({'id' : trip['id'], 'departure_time':departure_time, 'arrival_time':arrival_time, 'duration':duration,  'numberLegs' : len(trip['legs']), 
                    'modes': legs_mode, 'start_of_legs':start_legs, 'end_of_legs':end_legs, 'departure_times_leg':legs_start_time, 'arrival_times_leg':legs_end_time, 'stopPlaces':stopPlaces, 'TotNumberStops': len(stopPlaces)})
    return res

def convert_infos_to_dataframe(infos = None, df = None):

    """Converts result of get_trips_infos into dataframe
        ARG =  either provide the result of get_trips_infos, or the simple conversion to pandas dataframe"""

    if (df == None) and (infos != None):
        df = pd.json_normalize(infos, meta = list(infos[0].keys()))
    else:
        raise ValueError("Please provide at least one of infos or df")

    df = df.explode(['modes', 'start_of_legs', 'end_of_legs', 'departure_times_leg', 'arrival_times_leg'])
    df = df.drop(columns = ['id', 'stopPlaces', 'TotNumberStops', 'departure_time', 'arrival_time'])
    df['journey_nb'] = df.index.values + 1

    columns = ['journey_nb', 'start_of_legs', 'end_of_legs', 'departure_times_leg', 'arrival_times_leg', 'duration', 'numberLegs', 'modes']

    df = df[columns]
    new_columns = {'journey_nb': 'Journey_nbr', 'start_of_legs': 'Departure', 'end_of_legs': 'Arrival', 'departure_times_leg': 'Time_departure', 'arrival_times_leg': 'Time_arrival', 'duration': 'Journey_duration', 'numberLegs': 'Tot_nbr_stages', 'modes':'Transport_mode'}

    df.rename(columns=new_columns, inplace=True)
    return df

#def info_trips_to_data_frame(info_journey):

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
    return all_locations

def get_station_id(station):
    return station["id"]

def getDistanceFromLatLonInKm(lon1,lat1,lon2,lat2):
    """
    This function calculates the distance between 2 points according to their decimal angles.
    """
    R = 6371 # Radius of the earth in km
    dLat = deg2rad(lat2-lat1) 
    dLon = deg2rad(lon2-lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c # Distance in km
    return d

def deg2rad(deg):
    return deg * (math.pi/180)

def get_ids_of_places(places):
    df = pd.json_normalize(places['places'], meta = list(places['places'][0]))
    return df['id'].values.tolist()

def train_station_from_park_coords(park_coords):
    nearby_places = api.get_nearby_places(longitude=park_coords[0], latitude=park_coords[1], radius=1500, type="StopPlace", limit=50, includeVehicleModes=True)
    train_stations = get_train_stations(nearby_places)
    return [station["id"] for station in train_stations]

def divide_strings(full_string):
    if isinstance(full_string, float):
        return []
    else:
        return full_string.split("/")[1:]

def get_closest_train_stations_from_departure_by_car(departure_coords):
    """
    Get the identifiers of the 5 train stations that have a parking next to them and that are 
    closest to the departure point.
    """
    # Fetch mobilitat dataframe
    mobilitat_df_with_closest_stations = pd.read_csv("mobilitat_df_with_closest_stations.csv", index_col = 0)
    mobilitat_df_with_closest_stations["train_station_ids"] = mobilitat_df_with_closest_stations.apply(lambda x : divide_strings(x["train_station_ids"]), axis = 1)
    # Get distances to all parkings
    distances_park = mobilitat_df_with_closest_stations.apply(lambda x : getDistanceFromLatLonInKm(departure_coords[0],departure_coords[1],x["geopos.lon"],x["geopos.lat"]), axis = 1).values
    # Get indexes of 5 closest parkings
    park_indexes = distances_park.argsort()[:5]
    # Get identifiers of 5 closest stations 
    weird_list = [mobilitat_df_with_closest_stations["train_station_ids"].values[idx] for idx in park_indexes]
    return (weird_list[0]+weird_list[1]+weird_list[2]+weird_list[3]+weird_list[4])[0:5]

def get_coords(id, x):
    if id in x["train_station_ids"] :
        return ([x["geopos.lon"], x["geopos.lat"]]) 

def get_closest_train_park_coords(ids):
    """
    Gets the position of the parkings associated to the train stations with the given identifiers.
    """
    # Fetch mobilitat dataframe
    mobilitat_df_with_closest_stations = pd.read_csv("mobilitat_df_with_closest_stations.csv", index_col = 0)
    mobilitat_df_with_closest_stations["train_station_ids"] = mobilitat_df_with_closest_stations.apply(lambda x : divide_strings(x["train_station_ids"]), axis = 1)
    # Get coordinates of parkings
    closest_train_park_coords = []
    for id in ids:
        for row in mobilitat_df_with_closest_stations.apply(lambda x : get_coords(id, x), axis = 1):
            if row is not None:
                closest_train_park_coords.append(row)
                break
    return closest_train_park_coords

def get_drive_time_to_parking(origin, closest_train_park_coords):
    drive_time_to_parking = []
    for coords in closest_train_park_coords:
        start = {"longitude": origin[0], "latitude": origin[1]}
        parking = {"longitude": coords[0], "latitude": coords[1]}
        drive_time_to_parking.append(math.ceil(osm_helpers.get_itinerary_properties(start, parking)["duration"]/60))
    return drive_time_to_parking

def get_platform_coordinates(station_id, platform, sector= None):
    """Extracts coordinates of a given platform of a given station
    Args:
        station_id (string): ID of the station
        platform (int): number of the platform
        sector (string): optional, name of the sector(s) (eg. 'A' or 'A,B')
    Returns:
        list: coordinates vector of platform centroid (midpoint of the sectors) or of the station of no information of the station's is provided in the dataset
    """
    features = api.get_platform_features(int(station_id), platform, sector)

    if np.isin('status', list(features.keys())) and (features['status'] == 400):
        return api.get_stopplaces_by_id(station_id)['centroid']['coordinates']
    else:
        return features['features'][0]['geometry']['coordinates']
    
def get_walk_time_to_train_platform(closest_train_stations_ids, closest_train_park_coords):
    walk_time_to_train_platform = []
    for i, station in enumerate(closest_train_stations_ids):
        # Get the platform coords
        platform_coords = get_platform_coordinates(station, 1)
        # Compute the distance
        dist_park_platform = getDistanceFromLatLonInKm(platform_coords[0], platform_coords[1], closest_train_park_coords[i][0], closest_train_park_coords[i][1])
        walk_time_to_train_platform.append(math.ceil(dist_park_platform/5*60,)) # in minutes
    return walk_time_to_train_platform

def remove_trips(current_coord, arrival_coord, date, time, mode_to_departure):

    if mode_to_departure == 'CAR':
        nrst_dep_stations = get_closest_train_stations_from_departure_by_car(current_coord)
    elif mode_to_departure == 'FOOT':
        places = api.get_nearby_places(current_coord[0], current_coord[1], radius=1500, 
                                                                    type="StopPlace", limit=5, includeVehicleModes=False)
        print(places)
        nrst_dep_stations = get_ids_of_places(places)
    
    nrst_arr_stations = get_ids_of_places(api.get_nearby_places(arrival_coord[0], arrival_coord[1], radius=1500, 
                                                                type="StopPlace", limit=5, includeVehicleModes=False))
    #nearest stations are a lists of IDs

    journeys = []

    # if one of the trips proposed for each station proposes a stop by another of the nearest strations, rmove it
    for station_arr_id in nrst_arr_stations:
        for station_dep_id in nrst_dep_stations:
            journey = api.get_journey(origin=str(station_dep_id), destination = str(station_arr_id), date = date, time = time)
            infos = get_trips_infos(journey)

            for idx, trip in enumerate(infos):
                trip['stopPlaces'].pop(0)
                trip['stopPlaces'].pop(-1)
                if np.isin(station_dep_id, trip['stopPlaces']) :
                    journey['trips'].pop(idx)

                if np.isin(station_arr_id, trip['stopPlaces']) :
                    journey['trips'].pop(idx)

        journeys.append(journey)
    return journeys
                    
def get_parking_closest_to_station_with_name(station_name):
    # Get the id of the station
    id = [place["id"] for place in api.get_places(station_name)["places"] if place["name"]==station_name]
    # Get the coordinates of the station
    return get_closest_train_park_coords(ids=[id])

        



