import datetime
import json
import requests
import sys
from conf import conf


def get_flights_from_api(airport, json_data=None):
    """Get flights from the FlightRequests API. If json_data is provided (string),
    it will be used instead (debugging purposes)"""

    # First: Get raw response data
    data = {}
    if json_data is None:
        time = datetime.datetime.now()
        flight_stats_conf = conf()["flightStats"]

        # Can't use Request's parameter handling because most of these parameters are built into the URL path,
        # i.e. not passed as part of the querystring
        url = flight_stats_conf["urls"]["by_airport"].format(airport=airport,
                                                             year=time.year,
                                                             month=time.month,
                                                             day=time.day,
                                                             hour=time.hour,
                                                             app_id=flight_stats_conf["appId"],
                                                             app_key=flight_stats_conf["appKey"])
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to query flightstats for status of airport " + airport, file=sys.stderr)
            return
        data = response.json()
    else:
        data = json.loads(json_data)

    return data
