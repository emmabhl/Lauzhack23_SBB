from helpers import *
from api_requests import *

def run(data_user):
    api.use_token()

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
        
    trips = remove_trips(origin, destination, departure_day, departure_time, by)
    trips = flatten_dict(trips)
    infos = get_trips_infos(trips)

    if infos is not None:
        df = pd.json_normalize(infos, meta = list(infos[0].keys()))
    else:
        raise ValueError("Please provide at least one of infos or df")

    if by == 'CAR':
        for _, trip in df.iterrows():
            station_name = trip['start_of_legs'][0]
            station_id = station_name_to_id(station_name)
            closest_parking = get_closest_train_park_coords([station_id])
            driving_time = get_drive_time_to_parking(origin, closest_parking)[0]
            walk_time = 10 #get_walk_time_to_train_platform([station_id], closest_parking)[0]
            trip['duration'] = int(trip['duration']) + driving_time + walk_time
            trip['departure_time'] = trip['departure_time'] - pd.Timedelta(driving_time + walk_time, unit='minutes')
            trip['numberLegs'] = int(trip['numberLegs']) + 1
            trip['modes'] = ['CAR'] + trip['modes']
            trip['start_of_legs'] = [str(origin)] + trip['start_of_legs']
            trip['end_of_legs'] = [str(closest_parking)] + trip['end_of_legs']
            trip['departure_times_leg'] = [trip['departure_time']] + trip['departure_times_leg']
            trip['arrival_times_leg'] = [trip['departure_time'] + pd.Timedelta(driving_time + walk_time, unit='minutes')] + trip['arrival_times_leg']

    df = convert_infos_to_dataframe(df)

    transports_chosen = []
    for mode in list(transport_mean.keys()):
        if transport_mean[mode]:
            transports_chosen.append(mode)
    
    df[np.isin(df['Transport_mode'], transports_chosen)]
    non_good_df = df[~(df['Transport_mode'].isin(transports_chosen))]
    bad_journey=np.unique(non_good_df['Journey_nbr'].values)
    filtered_df=df[~df['Journey_nbr'].isin(bad_journey)]

    extract_best = filtered_df.groupby('Journey_nbr')['Time_arrival'].last().sort_values(ascending=False)
    # Keep only the 3 best journeys
    n_best = np.min([3, len(extract_best)])
    extract_best = extract_best.index[:n_best]
    final_df = filtered_df[filtered_df['Journey_nbr'].isin(extract_best)]

    return final_df