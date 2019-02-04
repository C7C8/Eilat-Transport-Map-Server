import datetime
import json
import requests
import sys

from conf import conf
import db


def get_flights_from_api(airport, json_data=None):
    """Get flights from the FlightRequests API and immediately cache them in the database"""

    # First: Get raw response data
    time = datetime.datetime.now()
    flight_stats_conf = conf()["flightStats"]

    # Can't use Request's parameter handling because most of these parameters are built into the URL path,
    # i.e. not passed as part of the querystring
    url = flight_stats_conf["urls"]["arrivalsByAirport"].format(airport=airport,
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

    # Data acquired; extract data we're actually interested in
    ret = list(map(lambda raw_flight: {
        "flightId": int(raw_flight["flightId"]),
        "arrivalId": str(raw_flight["arrivalAirportFsCode"]),
        "departureId": str(raw_flight["departureAirportFsCode"]),
        "airlineCode": str(raw_flight["carrierFsCode"]),
        "flightNumber": int(raw_flight["flightNumber"]),
        "departure_local": datetime.datetime.fromisoformat(raw_flight["departureDate"]["dateLocal"]),
        "arrival_local": datetime.datetime.fromisoformat(raw_flight["arrivalDate"]["dateLocal"])
    }, data["flightStatuses"]))

    db.save_flights(ret)
    return ret
