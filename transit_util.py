class Vehicle:
    def __init__(self):
        self.VehicleRef = -1
        self.LineRef = ""
        self.DirectionRef = -1
        self.PublishedLineName = ""
        self.OperatorRef = ""
        self.Agency = ""
        self.DestinationRef = -1
        self.Longitude = -1.0
        self.Latitude = -1.0

    def dict(self):
        return self.__dict__


class Stop:
    latitude = -1.0
    longitude = -1.0
    name = ""
    code = ""
    description = ""
    monitored_vehicles = []

    def getVehicles(self) -> [Vehicle]:
        return self.monitored_vehicles
