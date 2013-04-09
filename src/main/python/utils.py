
import os
from collections import namedtuple
from operator import attrgetter
from math import radians, cos, sin, asin, sqrt

Location = namedtuple('Location', 'timestamp hour minute second longitude latitude altitude accuracy speed_ms')
Acceleration = namedtuple('Acceleration', 'timestamp x y z')
Gyroscope = namedtuple('Gyroscope', 'timestamp x y z')
Orientation = namedtuple('Orientation', 'timestamp azimuth pitch roll')
Light = namedtuple('Light', 'timestamp lux')
LinearAcceleration = namedtuple('LinearAcceleration', 'timestamp x y z')
MagneticField = namedtuple('MagneticField', 'timestamp x y z')
Proximity = namedtuple('Proximity', 'timestamp distance')
LocationBucket = namedtuple('LocationBucket', 'start_location data_points end_location distance')


#10.0;14:14:21;145.08726507425308;-37.970201284624636;30.29998779296875;10.0;1.6263;5.8546796;3.6379354;3.161267;
def _convert_location(e):
    hhmmss = e[1].split(':')
    return Location(float(e[0]), int(hhmmss[0]), int(hhmmss[1]), int(hhmmss[2]), float(e[2]),
                    float(e[3]), float(e[4]), float(e[5]), float(e[6]))


def _convert_all_floats(e):
    return [float(_) for _ in e[:-1]]


input_files = {
    Location: ('LOCATION.txt', 1, _convert_location),
    Acceleration: ('ACCELEROMETER.txt', 2, lambda e: Acceleration(*_convert_all_floats(e))),
    Gyroscope: ('GYROSCOPE.txt', 2, lambda e: Gyroscope(*_convert_all_floats(e))),
    Orientation: ('ORIENTATION.txt', 3, lambda e: Orientation(*_convert_all_floats(e))),
    Light: ('LIGHT.txt', 2, lambda e: Light(*_convert_all_floats(e))),
    LinearAcceleration: ('LINEAR_ACCELERATION.txt', 2, lambda e: LinearAcceleration(*_convert_all_floats(e))),
    MagneticField: ('MAGNETIC_FIELD.txt', 2, lambda e: MagneticField(*_convert_all_floats(e))),
    Proximity: ('PROXIMITY.txt', 2, lambda e: Proximity(*_convert_all_floats(e))),
}


def _skip_lines_file(file, skip_count):
    if not os.path.isfile(file):
        print 'Not a file', file
        raise StopIteration()
    line_count = 0
    for e in (_.strip().split(';') for _ in open(file)):
        if line_count < skip_count:
            line_count += 1
            continue
        yield e


def read_entries(input_dir, input_type):
    file_name, skip_count, converter = input_files[input_type]
    file = os.path.join(input_dir, file_name)
    for e in _skip_lines_file(file, skip_count):
        yield converter(e)


def read_all_entries(input_dir, run_name):
    sub_dir = os.path.join(input_dir, str(run_name))
    data = []
    for input_type in input_files.keys():
        data.extend(read_entries(sub_dir, input_type))
    return sorted(data, key=attrgetter('timestamp'))


def filter_input_types(single_bucket, input_type, attribute):
    f = attrgetter(attribute)
    return [f(_) for _ in single_bucket.data_points if isinstance(_, input_type)]


# http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
# also includes the altitude change
# Location(timestamp=0.0, hour=9, minute=43, second=44, longitude=146.83176937513053, latitude=-36.332442658022046, altitude=367.5, accuracy=10.0, speed_ms=0.31275)
# Location(timestamp=1.0, hour=9, minute=43, second=45, longitude=146.8317690398544, latitude=-36.332443580031395, altitude=367.20001220703125, accuracy=10.0, speed_ms=0.2502)
# formula distance is 0.31841995232061665 which is about the speed from the first one
def haversine(origin, destination):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    lat1, lon1 = origin.latitude, origin.longitude
    lat2, lon2 = destination.latitude, destination.longitude
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    meters_2d = 6367 * c * 1000
    return sqrt(pow(meters_2d, 2) + pow(origin.altitude-destination.altitude, 2))


def bucketize(data):
    """returns a three element tuple: (start location, [ inbetween measurements ], end_location)"""
    start_loc = None
    entries = []
    end_loc = None
    for d in data:
        if isinstance(d, Location):
            if end_loc:
                yield LocationBucket(start_loc, entries, end_loc, haversine(start_loc,end_loc))
                start_loc, entries, end_loc = d, [], None
                continue
            if start_loc:
                end_loc = d
            else:
                start_loc = d
                end_loc = None
        else:
            if end_loc and end_loc.timestamp < d.timestamp:
                yield LocationBucket(start_loc, entries, end_loc, haversine(start_loc,end_loc))
                start_loc, entries, end_loc = end_loc, [], None
            entries.append(d)
    if end_loc:
        yield LocationBucket(start_loc, entries, end_loc, haversine(start_loc,end_loc))