import json
import urllib.request

import requests

import GTFS
from SIRI import StopMonitoringRequest, url


def get_stops():
    stops = []

    req = StopMonitoringRequest()
    codes = GTFS.get_stops()
    for code in codes:
        req.addRequest(code)

    try:
        stops = req.submit()
    except requests.exceptions.ConnectionError as e:
        print("Failed to connect to " + url)

    return stops


def print_vehicles(vehicles, stops):
    print('Found {} vehicles:'.format(len(vehicles)))
    for vehicleRef, vehicle in vehicles.items():
        print(vehicleRef)

    for stop in stops:
        for vehicle in stop.getVehicles():
            if vehicle.VehicleRef not in vehicles:
                print('Vehicle', vehicle.VehicleRef, 'not in list!')


def get_vehicles():
    vehicles = {}
    for stop in get_stops():
        for vehicle in stop.getVehicles():
            vehicles[vehicle.VehicleRef] = vehicle
    return vehicles


def get_vehicles_json():
    vehicle_objects = get_vehicles()
    vehicles_array = []
    for vehicleID, vehicle in vehicle_objects.items():
        vehicles_array.append(vehicle.__dict__)
    return vehicles_array


if __name__ == '__main__':
    print_vehicles(get_vehicles(), get_stops())
