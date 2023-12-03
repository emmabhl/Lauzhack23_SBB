from helpers import *
from api_requests import *

def run(data_user):


    origin = data_user["origin"]
    destination = data_user["destination"]
    departure_day = data_user["departure_day"]
    departure_time = data_user["departure_time"]
    transport_mean = data_user["transport_mean"]

    if ~transport_mean['CAR']:
        trips = remove_trips(origin, destination, departure_day, departure_time, 'FOOT')
    else: 
        if takes_car(origin):
            trips = remove_trips(origin, destination, departure_day, departure_time, 'CAR')
            for trip in trips:
                station_id = get_id_from_name(trip['start_of_legs'][0])
                closest_parking = get_closest_train_park_coords(station_id)
                driving_time = get_drive_time_to_parking(origin, closest_parking)
                walk_time = get_walk_time_to_train_platform(station_id, closest_parking)
                trip['duration'] = trip['duration'] + driving_time + walk_time
                trip['departure_time'] = trip['departure_time'] - driving_time - walk_time
                trip['numberLegs'] = trip['numberLegs'] + 1
                trip['modes'] = ['CAR'] + trip['modes']
                trip['start_of_legs'] = [str(origin)] + trip['start_of_legs']
                trip['end_of_legs'] = [str(closest_parking)] + trip['end_of_legs']
                trip['departure_times_legs'] = [trip['departure_time']] + trip['departure_times_legs']
                trip['arrival_times_legs'] = [trip['departure_time'] + driving_time + walk_time] + trip['arrival_times_legs']
                

            if ~transport_mean['TRAIN']:
        else: 
            trips = remove_trips(origin, destination, departure_day, departure_time, 'FOOT')

    infos = get_trips_infos(trips)
    df = convert_infos_to_dataframe(infos)



    transports_chosen = []
    for mode in list(transport_mean.key()):
        if transport_mean[mode]:
            transports_chosen.append(mode)
    
    df[np.isin(df['Transport_mode'], transports_chosen)]
    non_good_df = df[~(df['Transport_mode'].isin(transports_chosen))]
    bad_journey=np.unique(non_good_df['Journey_nbr'].values)
    filtered_df=df[~df['Journey_nbr'].isin(bad_journey)]

    final_df = filtered_df.sortby('Journey_duration').head(3)

    return final_df