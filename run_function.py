from helpers import *
from api_requests import *

def run(data_user):


    origin = data_user["origin"]
    destination = data_user["destination"]
    departure_day = data_user["departure_day"]
    departure_time = data_user["departure_time"]
    transport_mean = data_user["transport_mean"]

    if transport_mean == 'CAR':
        transport_mean = {'TRAIN':True,'BUS':True, 'FOOT':True, 'CAR':True, 'SHIP':True, 
                          'TRAMWAY':True,'CABLEWAY':True}
    elif transport_mean == 'FOOT':
        transport_mean = {'TRAIN':True,'BUS':True, 'FOOT':True, 'CAR':False, 'SHIP':True, 
                          'TRAMWAY':True,'CABLEWAY':True}

    if transport_mean['CAR'] and takes_car(origin):
        by = 'CAR'
    else:
        by = 'FOOT'

    def flatten_dict(trips):
        # flatten the trips 
        all_journeys = []
        if len(trips) > 1:
            for trip in trips:
                all_journeys += trip['trips']
            return {'trips': all_journeys}
        else:
            return trips
        
    trips = remove_trips(origin, destination, departure_day, departure_time, 'FOOT')
    trips = flatten_dict(trips)
    infos = get_trips_infos(trips)
    df = convert_infos_to_dataframe(infos)
    print(df)

    if by == 'CAR':
        station_name = df.groupby(trip['Departure'][0]


        for trip in df:
            station_id = [place["id"] for place in api.get_places(station_name)["places"] if place["name"]==station_name]
            closest_parking = get_parking_closest_to_station_with_name(station_name)
            driving_time = get_drive_time_to_parking(origin, closest_parking)
            walk_time = get_walk_time_to_train_platform(station_id, closest_parking)
            trip['Journey_duration'] = trip['Journey_duration'] + driving_time + walk_time
            trip['departure_time'] = trip['departure_time'] - driving_time - walk_time
            trip['Tot_nbr_stages'] = trip['Tot_nbr_stages'] + 1
            trip['Transport_mode'] = ['CAR'] + trip['Transport_mode']
            trip['Departure'] = [str(origin)] + trip['Departure']
            trip['Arrival'] = [str(closest_parking)] + trip['Arrival']
            trip['Time_departure'] = [trip['departure_time']] + trip['Time_departure']
            trip['Time_arrival'] = [trip['departure_time'] + driving_time + walk_time] + trip['Time_arrival']

    transports_chosen = []
    for mode in list(transport_mean.keys()):
        if transport_mean[mode]:
            transports_chosen.append(mode)
    
    df[np.isin(df['Transport_mode'], transports_chosen)]
    non_good_df = df[~(df['Transport_mode'].isin(transports_chosen))]
    bad_journey=np.unique(non_good_df['Journey_nbr'].values)
    filtered_df=df[~df['Journey_nbr'].isin(bad_journey)]

    final_df = filtered_df.sort_values(by='Journey_duration').head(3)

    return final_df