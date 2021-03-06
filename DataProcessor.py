import requests

import GTFS
from SIRI import StopMonitoringRequest, url


def get_stops():
    stops = []

    req = StopMonitoringRequest()
    codes = GTFS.get_stops()
    for code in codes:
        req.addRequest(str(code))
    try:
        stops = req.submit()
    except requests.exceptions.ConnectionError as e:
        print("Failed to connect to " + url)
    print('Found {} stops in Eilat!'.format(len(stops)))
    return stops


def print_vehicles():
    stops = get_stops()
    vehicles = get_vehicles(stops)
    print('Found {} vehicles:'.format(len(vehicles)))
    for vehicleRef, vehicle in vehicles.items():
        # print(vehicleRef)
        print(vehicleRef, vehicle.AgencyName, vehicle.AgencyURL)

    for stop in stops:
        for vehicle in stop.getVehicles():
            if vehicle.VehicleRef not in vehicles:
                print('Vehicle', vehicle.VehicleRef, 'not in list!')


def get_vehicles(stops=None):
    agencies = {}
    vehicles = {}
    if stops is None:
        stops = get_stops()
    for stop in stops:
        for vehicle in stop.getVehicles():
            if vehicle.AgencyID not in agencies:
                agency = GTFS.agency_by_id(vehicle.AgencyID)
                agencies[vehicle.AgencyID] = agency
            else:
                agency = agencies[vehicle.AgencyID]
            vehicle.AgencyName = agency[0]
            vehicle.AgencyURL = agency[1]
            vehicles[vehicle.VehicleRef] = vehicle
    return vehicles


def get_vehicles_json():
    vehicle_objects = get_vehicles()
    vehicles_array = []
    for vehicleID, vehicle in vehicle_objects.items():
        vehicles_array.append(vehicle.__dict__)
    return vehicles_array


if __name__ == '__main__':
    print_vehicles()
