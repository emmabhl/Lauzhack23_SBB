import requests

BASE_URL = "https://data.sbb.ch/api/explore/v2.1"

# Others URLs
dataset_url = BASE_URL + "/catalog/datasets/mobilitat/exports/json"


def get_dataset():
    return requests.get(dataset_url).json()