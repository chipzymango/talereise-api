import requests, json

def get_stop_id(stop_place): # finding stop place id using Geocoder API
    url = f"https://api.entur.io/geocoder/v1/autocomplete?text={stop_place}&lang=en"

    headers = {
      "ET-Client-Name": "chipzymango-talereise"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        features = data.get("features", [])
        if features:
            stop_id = features[0].get("properties", {}).get("id")
            return stop_id # get first stop id result
        else:
            return None # no stop ids could be found 
    else:
        print(f"request to get stop id failed with code: {response.status_code}")
        return None

def plan_journey(origin, destination, lat, long):
    pass

def get_next_departure(stop_place, line_number, front_text=None):
    pass