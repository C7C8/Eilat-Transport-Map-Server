import json
import sys


def conf():
    """Load config file if needed, or return cached result"""
    if hasattr(conf, "loaded"):
        return conf.loaded

    # Stored config; useful as a template for a conf file or as a fallback in case conf.json wasn't provided
    config = {
        "db": {
            "host": "localhost",
            "port": 3306,
            "user": "eilat_transport",
            "password": "password",
            "database": "eilat_transport"
        },
        "gtfs": {
            "url": "sqlite:///gtfs.sqlite"
        },
        "flightStats": {
            "urls": {
                "arrivalsByAirport": "https://api.flightstats.com/flex/flightstatus/rest/v2/json/airport/status/{airport}/arr/{year}/{month}/{day}/{hour}?appId={app_id}&appKey={app_key}&utc=false&numHours=6&codeType=IATA"
            },
            "appId": "CENSORED",
            "appKey": "CENSORED"
        }
    }
    try:
        with open("conf.json", "r") as file:
            config = json.load(file)
    except FileNotFoundError:
        print("Failed to load conf.json, falling back to internal default", file=sys.stderr)

    conf.loaded = config
    return config
