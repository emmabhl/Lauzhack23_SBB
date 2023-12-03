import streamlit as st
import datetime
import helpers as hlp
import api_requests as api
import geocoder
import pandas as pd
import numpy as np

api.use_token()

st.title('Your journey')

#to avoid errors in storing data which is not yet defined
origin = None
destination = None

current_pos=st.selectbox('Do you want to start from your current position?', ('Choose an option', 'Yes', 'No'))
if (current_pos=='Yes'): 
    #extract geolocalisation
    g = (geocoder.ip('me')).latlng
    origin = [g[1], g[0]]
elif(current_pos=='No'):
    origin_ = st.text_input(":blue[Please enter a stop place where you want to start]", "")
    if (origin_!="") : 
        #select from the multiple options
        possible_origin=hlp.get_stations(origin_)
        origin_name = st.selectbox(':blue[Please select the corresponding station:]', tuple(possible_origin['name']))
        origin = possible_origin[possible_origin['name']==origin_name]['centroid'].values[0]

current_pos_destintation=st.selectbox('Do you want to take your current position as destination?', ('Choose an option', 'Yes', 'No'))
if (current_pos_destintation=='Yes'): 
    #extract geolocalisation
    g_ = (geocoder.ip('me')).latlng
    destination = [g_[1], g_[0]]
elif(current_pos_destintation=='No'):
    destination_ = st.text_input(":blue[Where do you want to go?]", "")
    if (destination_!="") : 
        #select from the multiple options
        possible_destination=hlp.get_stations(destination_)
        destination_name = st.selectbox(':blue[Please select the corresponding station:]', tuple(possible_destination['name']))
        destination = possible_destination[possible_destination['name']==destination_name]['centroid'].values[0]


day = st.date_input('Departune day')
t = st.time_input('Departune time', key=datetime.datetime.now())

st.write('Which transport type would you like to use?')
col1, col2, col3 = st.columns(3)
train = col1.checkbox('Train', value=True)
bus = col2.checkbox('Bus', value=True)
foot = col3.checkbox('Foot', value=True)
car = col1.checkbox('Car', value=True)
boat = col2.checkbox('Boat', value=True)
metro_tram = col3.checkbox('Tramway/Metro', value=True)
funicular_cog_railway = col1.checkbox('Funicular/Cog railway', value=True)
bike = col2.checkbox('Bike', value=True)

#Store data in a dictionnary
data_user = {'origin':origin, 'destination':destination, 'departune_day':day, 'departune_time':t,
             'transport_mean':{'train':train,'bus':bus, 'foot':foot, 'car':car, 'boat':boat, 
                               'tramway/metro':metro_tram,'funicular_cog_railway':funicular_cog_railway, 
                               'bike':bike}}


st.markdown("""---""")

#Run notre algo


#st.button("Reset we pwjjn deJD O R  RR   n ef  nnrqj a fNWdMKWH W WEKW FLkdnekWRPJQK FSFJw lJN", type="primary")
#display the results

#test dataframe
result = pd.DataFrame(columns = [['Journey_nbr', 'Departure', 'Arrival', 'Time_departure', 'Time_arrival', 'Journey_duration','Transport_mode', 'Tot_nbr_stages', 'Tot_price' ]])
result['Journey_nbr']= [1,1,1]
result['Departure']=['A','B','C']
result['Arrival']=['B','C', 'D']
result['Time_departure']=['9:00', '10:00','11:00']
result['Time_arrival']=['9:30', '10:20','11:10']
result['Journey_duration']=[30,20,10]
result['Transport_mode']=['Train', 'Bus', 'Foot']
result['Tot_nbr_stages']=[3,3,3]
result['Tot_price']=[10,10,10]


#display the result
nbr_journey_tot = np.max(result['Journey_nbr'])
for n in  range (nbr_journey_tot):
    trips = result.iloc[np.where(result['Journey_nbr'] == (n+1))[0]]

    m = len(trips['Journey_nbr'])
    departure_time_journey=trips.iloc[0]['Time_departure']
    arrival_time_journey=trips.iloc[m-1]['Time_arrival']
    departure_spot= trips.iloc[0]['Departure']
    arrival_spot=trips.iloc[m-1]['Arrival']
    #duration=arrival_time_journey-departure_time_journey
    duration = 0

    list_transport=[]
    for i in range (len(result['Transport_mode'])):
        list_transport.append(result['Transport_mode'].loc[i].values[0])

    
    button_name ='Departure: ' + departure_spot +' ------ Arrival: ' + arrival_spot + ',   ' + str(duration) +' hours,   transports: '+ str(list_transport) + ',   Stages number :' + str(trips.iloc[0]['Tot_nbr_stages']) + ',   Price:' + str(trips.iloc[0]['Tot_price']) 


    if st.button(button_name):
        st.write(result)


