import time
from datetime import datetime
import xml.etree.ElementTree as ET


def siri_tag(name):
    return "siri:" + name


def set_attributes(element, attributes):
    for key, value in attributes.items():
        sub = ET.SubElement(element, siri_tag(key))
        sub.text = value


def get_time():
    return datetime.now().isoformat(timespec='milliseconds') + "+" \
           + str(int(time.localtime().tm_gmtoff / 3600)).zfill(2) + ":00"


class SIRI_Request:
    __timestamps = []
    __requestorRef = None
    __xml_root = None
    __xml_Request_node = None
    xml_request_node = []

    def timestamp(self, element):
        self.__timestamps.append(ET.SubElement(element, siri_tag('RequestTimestamp')))

    def set_time(self):
        timestamp_str = get_time()
        for timestamp in self.__timestamps:
            timestamp.text = timestamp_str

    def XML_base(self, service):
        self.__xml_root = ET.Element('S:Envelope')
        self.__xml_root.set('xmlns:S', 'http://schemas.xmlsoap.org/soap/envelope/')
        body = ET.SubElement(self.__xml_root, 'S:Body')
        siri_ws = ET.SubElement(body, 'siriWS:' + service)
        # siri_ws_dict = {
        #     {'xmlns:siriWS', 'http://new.webservice.namespace" xmlns='},
        #     {'xmlns', ''}
        # }
        # siri_ws.set(siri_ws_dict)
        set_attributes(siri_ws, {
            'xmlns:siriWS': 'http://new.webservice.namespace',
            'xmlns': '',
            'xmlns:ns4': 'http://www.ifopt.org.uk/ifopt',
            'xmlns:ns3': 'http://www.ifopt.org.uk/acsb',
            'xmlns:siri': 'http://www.siri.org.uk/siri'
        })

        request = ET.SubElement(siri_ws, 'Request')
        self.timestamp(request)
        requestor_ref = ET.SubElement(request, 'requestorRef')
        requestor_ref.text = 'EG898989'
        self.__xml_Request_node = request

    def addRequest(self, request_type):
        new_request = ET.SubElement(self.__xml_Request_node, siri_tag(request_type))
        new_request.set('version', '2.7')
        set_attributes(new_request, {
            'MessageIdentifier': '0',
            'PreviewInterval': 'PT30M',
            'StartTime': get_time(),
            'MonitoringRef': '32902',
            'MaximumStopVisits': '100',
        })
        self.timestamp(new_request)

    def dump(self):
        ET.dump(self.__xml_root)


class StopMonitoringRequest(SIRI_Request):

    def XML(self):
        self.XML_base('GetStopMonitoringService')
        # set_attributes(self.xml_request_node, )
        self.addRequest('StopMonitoringRequest')


if __name__ == '__main__':
    req = StopMonitoringRequest()
    req.XML()
    req.set_time()
    req.dump()
