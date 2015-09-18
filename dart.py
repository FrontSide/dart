#!/usr/bin/env python
"""
API info at http://api.irishrail.ie/realtime/
"""

import httplib
import urllib
import argparse
import json
from xml.etree import ElementTree

HOST = "api.irishrail.ie"
NS = {'irishrail': "http://%s/realtime/" % HOST}


class GoogleDistance():

    # Note that this API key is restricted to be used by me (my network) and will (most likely) not work for you.
    # You have to get your own
    GDAPI_KEY = "AIzaSyC20WYqcBzBYT8biVPl_pdwbQkED_atuko"
    GDAPI_DISTANCE_HOST = "maps.googleapis.com"
    GDAPI_LOCATION_HOST = "www.googleapis.com"
    GAPI_DISTANCE = "/maps/api/distancematrix/json" \
                    "?origins={ORIGIN_ADDRESS}&destinations={DESTINATION_ADDRESS}&mode=walking&key={API_KEY}"
    GAPI_LOCATION = "/geolocation/v1/geolocate?key={API_KEY}"

    def get_time_to_destination(self, destination_address, origin_address=None):
        if not origin_address:
            origin_address = self.get_location()
        json = get_json(self.GDAPI_DISTANCE_HOST,
                        self.GAPI_DISTANCE.format(ORIGIN_ADDRESS=origin_address.replace(" ", "+"),
                                                  DESTINATION_ADDRESS=destination_address.replace(" ", "+"),
                                                  API_KEY=self.GDAPI_KEY),
                        secure=True, method="POST")
        try:
            return json["rows"][0]["elements"][0]["duration"]["value"]/60 + 2  # Add 2 minute margin
        except KeyError:
            print("There seems to be now distance information available :(")
            return -1

    def get_location(self):
        json = get_json(self.GDAPI_LOCATION_HOST,
                        self.GAPI_LOCATION.format(API_KEY=self.GDAPI_KEY),
                        secure=True, method="POST")
        lat = json["location"]["lat"]
        lng = json["location"]["lng"]
        return "{LAT},{LNG}".format(LAT=lat, LNG=lng)


class Train():

    def __init__(self, dom):
        self.dom = dom
        self.type = self.dom.find('irishrail:Traintype', NS).text
        self.is_dart = self.type == "DART"
        self.destination = self.dom.find('irishrail:Destination', NS).text
        self.direction = self.dom.find('irishrail:Direction', NS).text
        self.due_in = int(self.dom.find('irishrail:Duein', NS).text)
        self.dep_time = self.dom.find('irishrail:Schdepart', NS).text

    def is_catchable(self, walk_time):
        return self.due_in > walk_time

    def when_to_leave(self, walk_time):
        if self.is_catchable(walk_time):
            return self.due_in - walk_time


def get_plain(host, path, secure=False, method="GET"):
    if secure:
        conn = httplib.HTTPSConnection(host)
    else:
        conn = httplib.HTTPConnection(host)
    conn.request(method, path, headers={"Content-Length": 0})
    resp = conn.getresponse()
    if resp.status != 200:
        raise Exception("HTTP Error: %s" % resp.read())
    plain = resp.read()
    conn.close()
    return plain


def get_json(host, path, secure=False, method="GET"):
    return json.loads(get_plain(host, path, secure, method))


def get_dom(host, path, secure=False, method="GET"):
    return ElementTree.fromstring(get_plain(host, path, secure, method))


def get_trains(station):
    path = "/realtime/realtime.asmx/getStationDataByNameXML" \
          "?StationDesc=%s" % urllib.quote(station)
    dom = get_dom(HOST, path)
    return [Train(train_dom) for train_dom in dom]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "departure_station",
        help="The departure station",
    )
    dir_grp = parser.add_mutually_exclusive_group(required=True)
    dir_grp.add_argument(
        "-n", "--northbound",
        action="store_const",
        const="Northbound",
        dest="direction",
        help="Use this if you're going northbound",
    )
    dir_grp.add_argument(
        "-s", "--southbound",
        action="store_const",
        const="Southbound",
        dest="direction",
        help="Use this if you're going southbound",
    )
    parser.add_argument(
        "-w", "--walk-time",
        help="The walk time (in minutes) from where you are to the "
             "departure station. "
             "If you omit this argument, your walk-time will be estimated based on your current location.",
        type=int,
    )
    args = parser.parse_args()

    trains = get_trains(args.departure_station)
    if len(trains) is 0:
        print "\nEither there are no trains leaving from %s Station " \
            "or the station doesn't exist (maybe a typo?)!\n" % args.departure_station
        return 1

    if args.walk_time:
        walk_time = args.walk_time
    else:
        walk_time = GoogleDistance().get_time_to_destination("%s Station | Dublin" % args.departure_station)
        if walk_time is -1:
            return 1
        print "\nYour estimated walking time to %s Station is %i minutes!\n" % (args.departure_station, walk_time)

    line_format = '{:<15s}  {:>6s}  {:>7s}  {:>6s}'

    print line_format.format("Destination", "Due", "Departs", "Leave", "")
    for train in trains:
        if train.is_dart and train.direction == args.direction:
            # catchable = "*" if train.is_catchable(WALK_TIME) else " "
            when_to_leave = train.when_to_leave(walk_time)
            leave_in = (
                "%s min" % when_to_leave
                if when_to_leave is not None
                else ""
            )
            print line_format.format(
                train.destination,
                "%s min" % train.due_in,
                train.dep_time,
                leave_in
            )


if __name__ == "__main__":
    main()
