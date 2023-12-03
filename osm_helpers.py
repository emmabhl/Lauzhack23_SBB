import requests

API_KEY = "5b3ce3597851110001cf6248e8ac8dbc875847c39a424bf63f13c88f"
ORS_URL = "https://api.openrouteservice.org"

DIRECTIONS_URL = ORS_URL + "/v2/directions/driving-car"
GET_URL = DIRECTIONS_URL + "?api_key=" + API_KEY


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