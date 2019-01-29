import json
import urllib.request

if __name__ == '__main__':
    my_url = "http://siri.motrealtime.co.il:8081/Siri/SiriServices?wsdl?key=EG898989"

    # url = "http://bustime.mta.info/api/siri/vehicle-monitoring.json?key=" + sys.argv[
    #     1] + "&VehicleMonitoringDetailLevel=calls&LineRef=" + sys.argv[2]
    response = urllib.request.urlopen(my_url)
    # Reading the response from the Site and Decoding it to UTF-8 Format
    data = response.read().decode("utf-8")
    # Converting the File to JSON Format
    # data = json.loads(data)
    print(data)
