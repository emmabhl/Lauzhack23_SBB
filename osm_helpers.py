import requests

API_KEY = "5b3ce3597851110001cf6248e8ac8dbc875847c39a424bf63f13c88f"
ORS_URL = "https://api.openrouteservice.org"

DIRECTIONS_URL = ORS_URL + "/v2/directions/driving-car"
GET_URL = DIRECTIONS_URL + "?api_key=" + API_KEY

SBB_MAPS_URL = " https://journey-maps-tiles.geocdn.sbb.ch/styles/base_bright_v2/style.json?api_key=8ff1e3c393578b6463f8a24b6baf0fd6"


def get_directions(start, destination):
    # Define the URL
    url = GET_URL + "&start=" + str(start['longitude']) + "," + str(start['latitude']) + "&end=" + str(destination['longitude']) + "," + str(destination['latitude'])

    # Get the directions
    r = requests.get(url)
    return r.json()

def get_itinerary_properties(start, destination):
    # Get the directions
    directions = get_directions(start, destination)

    # Get the route
    summary = directions['features'][0]['properties']['summary']
    itinerary = directions['features'][0]['geometry']['coordinates']
    
    return {'distance': summary['distance'], 'duration': summary['duration'], 'itinerary': itinerary}

def get_maps(start, destination, zoom=13):
    # Get the directions
    directions = get_directions(start, destination)

    # Get the route
    itinerary = directions['features'][0]['geometry']['coordinates']

    # Get the bounds
    min_longitude = min([itinerary[i][0] for i in range(len(itinerary))])
    max_longitude = max([itinerary[i][0] for i in range(len(itinerary))])
    min_latitude = min([itinerary[i][1] for i in range(len(itinerary))])
    max_latitude = max([itinerary[i][1] for i in range(len(itinerary))])

    # Define the URL
    url = SBB_MAPS_URL + "&zoom=" + str(zoom) + "&bbox=" + str(min_longitude) + "," + str(min_latitude) + "," + str(max_longitude) + "," + str(max_latitude)

    # Get the map
    r = requests.get(url)
    return r