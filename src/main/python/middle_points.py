import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
import sys
from operator import attrgetter

#Timestamp;Time;Longitude;Latitude;Altitude;Accuracy;Speed (m/s);Speed (km/h);Speed (mph);Speed (kts);


def read_location(reader):
    for e in (_.strip().split() for _ in reader):
        if e[1] == 'LOCATION':
            hhmmss = e[2].split(':')
            yield Location(float(e[0]), int(hhmmss[0]), int(hhmmss[1]), int(hhmmss[2]), float(e[3]),
                           float(e[4]), float(e[5]), float(e[6]), float(e[7]))


def get_attribute(data, attr_name):
    f = attrgetter(attr_name)
    return np.array([ f(_) for _ in data])


def main(args):
    input_file, output_file = args[:2]
    movement_data = [_ for _ in read_location(open(input_file))]
    timestamps = get_attribute(movement_data, 'timestamp')
    longitudes = get_attribute(movement_data, 'longitude')
    latitudes = get_attribute(movement_data, 'latitude')
    altitudes = get_attribute(movement_data, 'altitude')
    # spline order: 1 linear, 2 quadratic, 3 cubic ...
    order = 1
    # do inter/extrapolation
    s = InterpolatedUnivariateSpline(timestamps, longitudes, k=order)

    plt.figure()
    plt.plot(timestamps, longitudes, 'bo')
    y = s(timestamps)
    plt.plot(timestamps, y, 'rx')
    plt.show()

if __name__ == '__main__':
    main(sys.argv[1:])
