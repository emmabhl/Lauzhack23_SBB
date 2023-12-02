import requests

API_URL = "https://journey-service-int.api.sbb.ch:443"
TOKEN_URL = "https://login.microsoftonline.com/2cda5d11-f0ac-46b3-967d-af1b2e1bd01a/oauth2/v2.0/token"
CLIENT_SECRET = "MU48Q~IuD6Iawz3QfvkmMiKHtfXBf-ffKoKTJdt5"
CLIENT_ID = "f132a280-1571-4137-86d7-201641098ce8"
SCOPE = "c11fa6b1-edab-4554-a43d-8ab71b016325/.default"

# Others URLs
trips_url = API_URL + "/v3/trips/by-origin-destination"
station_url = API_URL + "/v3/places"


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
    return requests.post(trips_url, json=request_body, headers={"Authorization": "Bearer " + token}).json()

def get_places(nameMatch):
    request_body = {
        "nameMatch": nameMatch}
    return requests.get(station_url, params=request_body, headers={"Authorization": "Bearer " + token}).json()
