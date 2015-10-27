# DART
The DART is a train system in Dublin (Dublin Area Rapid Transit)

It has an API, and so this is a script for judging when to leave for the DART.

It will tell you the next few trains, their destination, departure time, and
when you should leave your current location to catch them.

Note that the Google API only works with your own API Key!

## Help
```
$ ./dart.py --help
usage: dart.py [-h] (-n | -s) [-w WALK_TIME] departure_station

positional arguments:
  departure_station     The departure station

optional arguments:
-h, --help            show this help message and exit
-n, --northbound      Use this if you're going northbound
-s, --southbound      Use this if you're going southbound
-w WALK_TIME, --walk-time WALK_TIME
                      The walk time (in minutes) from where you are to the
                      departure station. If you omit this argument, your
                      walk-time will be estimated based on your current
                      location.
--google-api-key G_API_KEY
                      Your Google API Key for the Location and Distance
                      Service.

```

## Example
You want to leave from Tara Street, go southbound.
```
$ ./dart.py "Tara Street" --southbound
Destination     Due  Departs   Leave
Bray         14 min    19:13   4 min
Greystones   29 min    19:28  19 min
Bray         44 min    19:43  34 min
Greystones   59 min    19:58  49 min
Bray         74 min    20:13  64 min
Greystones   90 min    20:29  80 min
```

You want to leave from Howth and you know that your walk-time to the station
is 14 min.
```
$ ./dart.py "Howth" --southbound -w 14
Destination         Due  Departs   Leave
Bray             26 min    12:15  12 min
Bray             56 min    12:45  42 min
Bray             86 min    13:15  72 min
```
