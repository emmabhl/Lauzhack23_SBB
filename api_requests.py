import requests

API_URL = "https://journey-service-int.api.sbb.ch:443"
TOKEN_URL = "https://login.microsoftonline.com/2cda5d11-f0ac-46b3-967d-af1b2e1bd01a/oauth2/v2.0/token"
CLIENT_SECRET = "MU48Q~IuD6Iawz3QfvkmMiKHtfXBf-ffKoKTJdt5"
CLIENT_ID = "f132a280-1571-4137-86d7-201641098ce8"
SCOPE = "c11fa6b1-edab-4554-a43d-8ab71b016325/.default"

# Others URLs
TRIPS_URL = API_URL + "/v3/trips/by-origin-destination"
NEARBY_PLACES_URL = API_URL + "/v3/places/by-coordinates-geojson"
TRANSPORTS_FROM_ID_URL = API_URL + "/v3/vehicle-journeys/by-departure/"

def get_token():
    params = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": SCOPE
    }
    
    return requests.post(TOKEN_URL, data=params).json()

def use_token():
    global token
    token = get_token()["access_token"]

def get_journey(origin, destination, date, time):
    request_body = {
        "origin": origin,
        "destination": destination,
        "date": date,
        "time": time,
    }

    return requests.post(TRIPS_URL, json=request_body, headers={"Authorization": "Bearer " + token}).json()

def get_nearby_places(longitude, latitude, radius, limit, type, includeVehicleModes):
    params = {
        'center': f"[ {longitude}, {latitude} ]",
        'radius': radius,
        'limit': limit,
        'type': type, # Get only stop places = train stops
        'includeVehicleModes':includeVehicleModes} 
    return requests.get(NEARBY_PLACES_URL, params=params, headers={"Authorization": "Bearer " + token}).json()

def get_place_from_id(id):
    return requests.get(TRANSPORTS_FROM_ID_URL+id, headers={"Authorization": "Bearer " + token}).json()
