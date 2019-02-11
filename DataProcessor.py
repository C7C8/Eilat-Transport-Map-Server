import json
import urllib.request

import requests

from GTFS import get_stops
from SIRI import StopMonitoringRequest, url


def get_stops():
    stops = []

    # if __name__ == '__main__':
    req = StopMonitoringRequest()
    codes = get_stops()
    for code in codes:
        req.addRequest(code)

    try:
        stops = req.submit()
    except requests.exceptions.ConnectionError as e:
        print("Failed to connect to " + url)

    # for vehicleRef, vehicle in vehicles.items():
    #     print(vehicleRef)

    # for stop in stops:
    #     for vehicle in stop.getVehicles():
    #         if vehicle.VehicleRef not in vehicles:
    #             print('Vehicle', vehicle.VehicleRef, 'not in list!')

    return stops


def get_vehicles():
    vehicles = {}
    for stop in get_stops():
        # print(stop.code)
        for vehicle in stop.getVehicles():
            vehicles[vehicle.VehicleRef] = vehicle
            # print('\t', i, '', vehicle.VehicleRef)

    # print('Found {} vehicles:'.format(len(vehicles)))
    return vehicles


def get_vehicles_json():
    vehicles_obj = get_vehicles()
    vehicles_dict = {}
    for vehicleID, vehicle in vehicles_obj.items():
        vehicles_dict[vehicleID] = vehicle.__dict__
    return json.dumps(vehicles_dict)
