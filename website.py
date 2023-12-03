import streamlit as st
import datetime
import helpers as hlp
import api_requests as api
import geocoder

api.use_token()

st.title('Your journey')

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

