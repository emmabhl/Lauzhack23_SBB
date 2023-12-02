import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

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

def trip_durations(trips):
    print([trip["duration"] for trip in trips])
    return [string_to_actual_time(trip["duration"]) for trip in trips]

def departure_to_time(trip):
    """Returns the departure time of a trip"""
    departure = trip['legs'][0]['serviceJourney']['stopPoints'][0]['departure']['timeAimed']
    departure = datetime.strptime(departure, '%Y-%m-%dT%H:%M:%S%z')
    departure = departure.replace(tzinfo=None)
    return departure

def get_departures_times(trips):
    return [departure_to_time(trip) for trip in trips]