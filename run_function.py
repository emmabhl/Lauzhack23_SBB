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