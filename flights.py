import datetime
from dateutil import parser
import requests
import sys
from conf import conf
import db


def get_flights_from_api(airport, json_data=None):
    """Get flights from the FlightRequests API and immediately cache them in the database"""

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

    # TODO: Probably change this so we're not needlessly constructing dictionaries from data
    #  already provided by the server. Doing it this way started out as a way to make the db
    #  less reliant on how the FlightStats api provides data to us, but now I'm not so sure
    #  it's a good idea.

    # Data acquired; extract flights
    ret = list(map(lambda flight: {
        "flightId": int(flight["flightId"]),
        "arrivalId": str(flight["arrivalAirportFsCode"]),
        "departureId": str(flight["departureAirportFsCode"]),
        "airlineCode": str(flight["carrierFsCode"]),
        "flightNumber": int(flight["flightNumber"]),
        "departure_local": parser.parse(flight["departureDate"]["dateLocal"]),
        "arrival_local": parser.parse(flight["arrivalDate"]["dateLocal"])
    }, data["flightStatuses"]))

    # In order to shove things into the db we need to extract relevant airports & airlines
    # for better readability on the front end

    if "airports" in data["appendix"].keys():
        airports = list(map(lambda raw_airport: {
            "name": raw_airport["name"],
            "city": raw_airport["city"],
            "country": raw_airport["countryName"],
            "fs": raw_airport["fs"],
            "iata": raw_airport["iata"]
        }, data["appendix"]["airports"]))
        db.save_airports(airports)

    if "airlines" in data["appendix"].keys():
        airlines = list(map(lambda airline: {
            "name": airline["name"],
            "fs": airline["fs"],
            "iata": airline["iata"]
        }, data["appendix"]["airlines"]))
        db.save_airlines(airlines)

    db.save_flights(ret)
    return ret


print(len(get_flights_from_api("ETH")))
print(len(get_flights_from_api("ETM")))
print(len(get_flights_from_api("VDA")))
