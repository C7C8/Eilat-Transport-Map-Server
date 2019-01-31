import time
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, dump, ElementTree, fromstring, tostring
import requests

regex = '(?<=<)\\w+:'

mot_siri = 'http://siri.motrealtime.co.il:8081/Siri/SiriServices'
icarus_siri_proxy = 'http://siri.motrealtime.icarusnet.me/Siri/SiriServices'

url = icarus_siri_proxy
ns0 = 'http://schemas.xmlsoap.org/soap/envelope/'
ns1 = 'http://new.webservice.namespace'
ns3 = 'http://www.ifopt.org.uk/acsb'
ns4 = 'http://www.ifopt.org.uk/ifopt'
ns_siri = 'http://www.siri.org.uk/siri'
ns_siriWS = 'http://new.webservice.namespace'
nsS = 'http://schemas.xmlsoap.org/soap/envelope/'
prefix = '<?xml version="1.0" ?>'


def xp_ns(tags):
    path = './'
    for ns, tag in tags:
        path += ('{' + ns + '}' if ns is not None else '') + tag + '/'
    return path[:-1]


def siri_tag(name):
    return "siri:" + name


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
        requestor_ref.text = 'EG898989'
        self.__xml_main_Request_node = request

    def addRequest(self, request_type: str) -> Node:
        new_request = self.__xml_main_Request_node.add_child(siri_tag(request_type))
        new_request.set('version', '2.7')
        req_id = new_request.add_child('MessageIdentifier')
        req_id.text = '0'
        self.add_timestamp(new_request)
        return new_request

    def print(self):
        dump(self.xml_root_node)
        print(self)

    def write(self):
        tree = ElementTree(self.xml_root_node)
        tree.write('req.xml', None, True)

    def __send(self):
        self.set_time()
        print('<?xml version="1.0" ?>' + self.xml_root_node.tostring())
        response = requests.post(url, data=prefix + self.xml_root_node.tostring(),
                                 headers={'Content-Type': 'text/xml'})
        return response.status_code, response.text

    def response(self):
        data = self.__send()
        self.response_code = data[0]
        self.xml_response_root = fromstring(data[1])
        path = xp_ns([(ns0, 'Body'), (ns1, self.__service + 'Response'), (None, 'Answer')])
        answer = self.xml_response_root.findall(path)[0]
        if answer is None:
            print("Error: NoneType for ElementTree")
            return
        # print('ANSWER:', tostring(answer))
        path = xp_ns([(ns_siri, 'Status')])
        status = answer.findall(path)[0].text
        if status == 'true':
            print("Request was successful!")


class StopMonitoringRequest(SIRI_Request):
    def __init__(self, preview_interval, ref, max_visits='100', start_time=get_time()):
        super().__init__('GetStopMonitoringService')
        self.preview_interval = preview_interval
        self.ref = ref
        self.start_time = start_time
        self.max_visits = max_visits
        smr = self.addRequest('StopMonitoringRequest')
        smr.add_children({
            'PreviewInterval': self.preview_interval,
            'StartTime': self.start_time,
            'MonitoringRef': self.ref,
            'MaximumStopVisits': self.max_visits,
        })
    # def build_xml(self):


if __name__ == '__main__':
    req = StopMonitoringRequest('PT30M', '32902')
    req.set_time()
    try:
        req.response()
    except requests.exceptions.ConnectionError as e:
        print("Failed to connect to " + url)
