class Vehicle:
    def __init__(self):
        self.VehicleRef = -1
        self.LineRef = ""
        self.DirectionRef = -1
        self.PublishedLineName = ""
        self.OperatorRef = ""
        self.Agency = ""
        self.DestinationRef = -1
        self.Longitude = float
        self.Latitude = float

    def dict(self):
        return self.__dict__


class Stop:
    latitude = float
    longitude = float
    name = str
    code = ""
    description = str
    monitored_vehicles = []

    def getVehicles(self) -> [Vehicle]:
        return self.monitored_vehicles
