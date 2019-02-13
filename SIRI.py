import time
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, dump, ElementTree, fromstring, tostring
import requests

from transit_util import Stop, Vehicle

regex = '(?<=<)\\w+:'

mot_siri = 'http://siri.motrealtime.co.il:8081/Siri/SiriServices'
icarus_siri_proxy = 'http://siri.motrealtime.icarusnet.me/Siri/SiriServices'

url = icarus_siri_proxy

username = 'EG898989'
# username = 'FOO'
ns0 = 'http://schemas.xmlsoap.org/soap/envelope/'
ns1 = 'http://new.webservice.namespace'
ns3 = 'http://www.ifopt.org.uk/acsb'
ns4 = 'http://www.ifopt.org.uk/ifopt'
ns_siri = 'http://www.siri.org.uk/siri'
ns_siriWS = 'http://new.webservice.namespace'
nsS = 'http://schemas.xmlsoap.org/soap/envelope/'
prefix = '<?xml version="1.0" ?>'


def xpath(tags):
    path = './'
    for ns, tag in tags:
        path += ('{' + ns + '}' if ns is not None else '') + tag + '/'
    return path[:-1]


def xdir(ns, tag):
    return xpath([(ns, tag)])


def siri_dir(tag):
    return xdir(ns_siri, tag)


def siri_tag(name):
    return "siri:" + name


def node_tag(node, tag):
    try:
        return node.findall(tag)[0].text

    except IndexError:
        # print('Failed to get ' + tag + ' from node:')
        # dump(node)
        pass


def get_time():
    return datetime.now().isoformat(timespec='milliseconds') + "+" \
           + str(int(time.localtime().tm_gmtoff / 3600)).zfill(2) + ":00"


class Node(Element):
    def __init__(self, text):
        super().__init__(text)

    def set(self, a, b=None):
        if type(a) is dict:
            for key, value in a.items():
                self.set(key, value)
        else:
            super().set(a, b)

    def add_child(self, tag: str, value: str = "") -> Element:
        sub = Node(tag)
        self.append(sub)
        sub.text = value
        return sub

    def add_children(self, children: dict) -> None:
        for tag, value in children.items():
            self.add_child(tag, value)

    def tostring(self):
        return tostring(self, encoding='unicode', method='xml')


class SIRI_Request:
    __timestamps = []
    __requestorRef = None
    xml_root_node = None
    __xml_main_Request_node = None
    xml_siri_request_nodes = []
    xml_response_root = None
    response_code = None
    __service = None

    def __init__(self, get_service):
        self.__service = get_service
        self.build_xml()

    def add_timestamp(self, element):
        self.__timestamps.append(SubElement(element, siri_tag('RequestTimestamp')))

    def set_time(self):
        timestamp_str = get_time()
        for timestamp in self.__timestamps:
            timestamp.text = timestamp_str

    def build_xml(self):
        self.xml_root_node = Node('S:Envelope')
        self.xml_root_node.set('xmlns:S', nsS)
        body = self.xml_root_node.add_child('S:Body')
        siri_ws = body.add_child('siriWS:' + self.__service)
        siri_ws.set({'xmlns:siriWS': ns_siriWS, 'xmlns': '', 'xmlns:ns4': ns4, 'xmlns:ns3': ns3, 'xmlns:siri': ns_siri})
        request = siri_ws.add_child('Request')
        self.add_timestamp(request)
        requestor_ref = SubElement(request, 'RequestorRef')
        requestor_ref.text = username
        self.__xml_main_Request_node = request

    def addRequest(self, request_type: str) -> Node:
        new_request = self.__xml_main_Request_node.add_child(siri_tag(request_type))
        new_request.set('version', '2.7')
        req_id = new_request.add_child('MessageIdentifier')
        req_id.text = '0'
        self.add_timestamp(new_request)
        return new_request

    def write(self):
        tree = ElementTree(self.xml_root_node)
        tree.write('req.xml', None, True)

    def submit(self):
        self.set_time()
        # print('<?xml version="1.0" ?>' + self.xml_root_node.tostring())
        response = requests.post(url, data=prefix + self.xml_root_node.tostring(),
                                 headers={'Content-Type': 'text/xml'})
        # return response.status_code, response.text

        # self.response_code = response.status_code
        self.xml_response_root = fromstring(response.text)
        path = xpath([(ns0, 'Body'), (ns1, self.__service + 'Response'), (None, 'Answer')])
        answer = self.xml_response_root.findall(path)[0]
        if answer is None:
            print("Error: NoneType for ElementTree")
            return
        # print('ANSWER:')
        # dump(answer)
        path = xpath([(ns_siri, 'Status')])
        status = answer.findall(path)[0]
        # print(status)
        if not status.text == 'true':
            path = xpath([(ns_siri, 'ErrorCondition'), (ns_siri, 'Description')])
            description = answer.findall(path)[0]
            print("Request failed: " + description.text)
            return

        StopMonitoringDeliveries = []

        for smd in answer.findall(xdir(ns_siri, 'StopMonitoringDelivery')):
            StopMonitoringDeliveries.append(smd)

        return StopMonitoringDeliveries

    def print(self):
        dump(self.xml_root_node)


class StopMonitoringRequest(SIRI_Request):
    preview_interval = str
    start_time = str
    max_visits = str

    def __init__(self, preview_interval='PT30M', max_visits='100', start_time=get_time()):
        super().__init__('GetStopMonitoringService')
        self.preview_interval = preview_interval
        self.start_time = start_time
        self.max_visits = max_visits

    def addRequest(self, ref):
        smr = super().addRequest('StopMonitoringRequest')
        smr.add_children({
            'PreviewInterval': self.preview_interval,
            'StartTime': self.start_time,
            'MonitoringRef': ref,
            'MaximumStopVisits': self.max_visits,
        })

    def submit(self):
        siri_stops = []
        data = super().submit()
        for stop_monitoring_delivery in data:
            stop = Stop()
            for monitored_stop_visit in stop_monitoring_delivery.findall(siri_dir('MonitoredStopVisit')):
                if stop.code == "":
                    stop.code = monitored_stop_visit.findall(siri_dir('MonitoringRef'))[0].text

                vehicle = Vehicle()

                for vehicle_node in monitored_stop_visit.findall(siri_dir('MonitoredVehicleJourney')):
                    vehicle.VehicleRef = node_tag(vehicle_node, siri_dir('VehicleRef'))
                    vehicle.LineRef = node_tag(vehicle_node, siri_dir('LineRef'))
                    vehicle.DirectionRef = node_tag(vehicle_node, siri_dir('DirectionRef'))
                    vehicle.PublishedLineName = node_tag(vehicle_node, siri_dir('PublishedLineName'))
                    vehicle.OperatorRef = node_tag(vehicle_node, siri_dir('OperatorRef'))
                    vehicle.DestinationRef = node_tag(vehicle_node, siri_dir('DestinationRef'))
                    for location in vehicle_node.findall(siri_dir('VehicleLocation')):
                        vehicle.Longitude = float(node_tag(location, siri_dir('Longitude')))
                        vehicle.Latitude = float(node_tag(location, siri_dir('Latitude')))
                    vehicle.AgencyID = node_tag(vehicle_node, siri_dir('OperatorRef'))
                if vehicle.Latitude != -1 and vehicle.Longitude != -1:
                    stop.monitored_vehicles.append(vehicle)
            siri_stops.append(stop)

        return siri_stops


if __name__ == '__main__':
    req = StopMonitoringRequest()
    req.addRequest('32902')
    try:
        stops = req.submit()
    except requests.exceptions.ConnectionError as e:
        print("Failed to connect to " + url)
