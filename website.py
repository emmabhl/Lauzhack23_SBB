import streamlit as st
import datetime

st.title('Your journey')

origin = st.text_input("Where do you want to start?", "")
destination = st.text_input("Where do you want to go?", "")

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
if (origin==""and destination==""): st.write('Please provide details of your journey')
elif (origin=="" and destination!=""): st.write('Please provide a starting point')
elif (destination==""and origin!=""): st.write('Please provide a destination')

#Run notre algo

