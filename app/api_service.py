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
            print("Found stop id: " + str(stop_id))
            return stop_id # get first stop id result
        else:
            print("No stop id's found")
            return None # no stop ids could be found 
    else:
        print(f"request to get stop id failed with code: {response.status_code}")


def get_next_departure(stop_id, line_number, front_text=None):
    base_url = "https://api.entur.io/journey-planner/v3/graphql"

    query = """
    {
    stopPlace(id: "NSR:StopPlace:{0}") {
        id
        name
        estimatedCalls(timeRange: 72100, numberOfDepartures: 10) {     
        realtime
        aimedArrivalTime
        aimedDepartureTime
        expectedArrivalTime
        expectedDepartureTime
        actualArrivalTime
        actualDepartureTime
        date
        forBoarding
        forAlighting
        destinationDisplay {
            frontText
        }
        quay {
            id
        }
        serviceJourney {
            journeyPattern {
            line {
                id
                name
                transportMode
            }
            }
        }
        }
    }
    }
    """.format(stop_id)

    headers = {
        "ET-Client-Name": "chipzymango-talereise"
    }

    response = requests.post(
        base_url,
        headers=headers,
        json={"query": query}
    )

    if response.status_code == 200:
        data = response.json()
        stop_place = data.get("stopPlace", {}):
        if stop_place:
            stop_name = stop_place.get("name", "undefined")
            results = stop_place.get("estimatedCalls", [])
            if results: # if there were results
                first_departure = results[0]["expectedDepartureTime"]
                print("first departure on " + str(stop_name) + " is: " + str(first_departure))
                return first_departure
            else:
                print("No departure timings were found from this query.")
        else:
            print("Stop place couldn't be found")

    else:
        print(f"request to get response from journeyplanner failed with code: {response.status_code}")

def plan_journey(origin, destination, lat, long):
    pass