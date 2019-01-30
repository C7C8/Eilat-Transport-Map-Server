import time
from datetime import datetime
from xml.etree.ElementPath import findtext
from xml.etree.ElementTree import Element, SubElement, dump, ElementTree, fromstring
import requests

mot_siri = 'http://siri.motrealtime.co.il:8081/Siri/SiriServices'
icarus_siri_proxy = 'http://siri.motrealtime.icarusnet.me/Siri/SiriServices'

url = icarus_siri_proxy


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
        from xml.etree.ElementTree import tostring
        return tostring(self, encoding='unicode', method='xml')


class SIRI_Request:
    __timestamps = []
    __requestorRef = None
    xml_root_node = None
    __xml_main_Request_node = None
    xml_siri_request_nodes = []
    xml_response_root = None
    response_code = None

    def add_timestamp(self, element):
        self.__timestamps.append(SubElement(element, siri_tag('RequestTimestamp')))

    def set_time(self):
        timestamp_str = get_time()
        for timestamp in self.__timestamps:
            timestamp.text = timestamp_str

    def build_xml(self, service):
        self.xml_root_node = Node('S:Envelope')
        self.xml_root_node.set('xmlns:S', 'http://schemas.xmlsoap.org/soap/envelope/')
        body = self.xml_root_node.add_child('S:Body')
        siri_ws = body.add_child('siriWS:' + service)
        siri_ws.set({
            'xmlns:siriWS': 'http://new.webservice.namespace',
            'xmlns': '',
            'xmlns:ns4': 'http://www.ifopt.org.uk/ifopt',
            'xmlns:ns3': 'http://www.ifopt.org.uk/acsb',
            'xmlns:siri': 'http://www.siri.org.uk/siri'
        })
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
        response = requests.post(url, data='<?xml version="1.0" ?>' + self.xml_root_node.tostring(),
                                 headers={'Content-Type': 'text/xml'})
        return response.status_code, response.text

    def response(self):
        data = self.__send()
        self.response_code = data[0]
        self.xml_response_root = fromstring(data[1])
        dump(self.xml_response_root)
        # answer = findtext(self.xml_response_root, 'Answer')
        # dump(answer)
        # status = findtext(answer, 'Status')
        # dump(status)


class StopMonitoringRequest(SIRI_Request):
    def __init__(self, preview_interval, ref, max_visits='100', start_time=get_time()):
        super().__init__()
        self.preview_interval = preview_interval
        self.ref = ref
        self.start_time = start_time
        self.max_visits = max_visits
        super().build_xml('GetStopMonitoringService')
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
    req.response()
    # data = req.__send()[1]
    # dump(dataTree)
    # print(data)
    # req.send()
    # dump(req.xml_root)
