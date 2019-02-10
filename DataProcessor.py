import json
import urllib.request

import requests

from GTFS import get_stops
from SIRI import StopMonitoringRequest, url

# if __name__ == '__main__':
req = StopMonitoringRequest()
codes = get_stops()
for code in codes:
    req.addRequest(code)
stops = []
try:
    stops = req.submit()
except requests.exceptions.ConnectionError as e:
    print("Failed to connect to " + url)

vehicles = {}

for stop in stops:
    # print(stop.code)
    for vehicle in stop.getVehicles():
        vehicles[vehicle.VehicleRef] = vehicle
        # print('\t', i, '', vehicle.VehicleRef)

print('Found {} vehicles:'.format(len(vehicles)))
# for vehicleRef, vehicle in vehicles.items():
#     print(vehicleRef)


for stop in stops:
    for vehicle in stop.getVehicles():
        if vehicle.VehicleRef not in vehicles:
            print('Vehicle', vehicle.VehicleRef, 'not in list!')
