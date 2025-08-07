import requests, json
from datetime import datetime
import pytz

def get_stop_id(stop_place): # finding stop place id using Geocoder API
    url = f"https://api.entur.io/geocoder/v1/autocomplete?text={stop_place}&lang=no&layers=venue&boundary.county_ids=KVE:TopographicPlace:03"

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

def format_departure_time(departure_time_iso):
    dt_departure_time = datetime.fromisoformat(departure_time_iso)
    current_time = datetime.now(pytz.timezone("Europe/Oslo"))
    time_diff = dt_departure_time - current_time
    minutes_diff = int(time_diff.total_seconds() // 60)

    if minutes_diff < 1:
        return "Nå"
    elif minutes_diff > 15:
        return dt_departure_time.strftime("%H:%M")
    return f"{minutes_diff} min"
    
def get_next_departure(stop_id, line_number, front_text=None):
    base_url = "https://api.entur.io/journey-planner/v3/graphql"

    query = """
    {{
        stopPlace(id: "{0}") {{
            id
            name
            estimatedCalls(timeRange: 72100, numberOfDepartures: 50) {{     
                expectedDepartureTime
                serviceJourney {{
                    line {{
                        publicCode
                        transportMode
                    }}
                }}
                destinationDisplay {{
                    frontText
                }}
            }}
        }}
    }}
    """.format(stop_id)

    headers = {
        "ET-Client-Name": "chipzymango-talereise"
    }

    response = requests.post(base_url, headers=headers, json={"query": query})

    if response.status_code != 200:
        return "the request to entur API failed"

    data = response.json() 
    stop_place = data.get("data", {}).get("stopPlace")
    if not stop_place:
        return "the stop was not found"
    
    results = stop_place.get("estimatedCalls", [])
    if not results:
        return "there are currently no departures in this stop"

    for result in results:
        line = result.get("serviceJourney", {}).get("line", {})
        destination = result.get("destinationDisplay", {}).get("frontText", "")

        if str(line.get("publicCode")) == str(line_number):
            if front_text:
                if destination.replace(" T", "").lower() != front_text.lower():
                    continue

            departure_time = result.get("expectedDepartureTime")
            return format_departure_time(departure_time)

    return "A matching departure couldn't be found"