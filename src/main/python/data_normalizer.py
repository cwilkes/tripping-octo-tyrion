__author__ = 'cwilkes'

import sys
import os
from operator import itemgetter




def get_input_directories(input_dir):
    for _ in os.listdir(input_dir):
        ret = os.path.join(input_dir, _)
        if os.path.isdir(ret):
            # all directories have the accelerometer file
            acc_file = os.path.join(ret, 'ACCELEROMETER.txt')
            if os.path.isfile(acc_file):
                yield (_, ret)


def skip_lines_file(file, skip_count):
    if not os.path.isfile(file):
        print 'Not a file', file
        raise StopIteration()
    line_count = 0
    for e in (_.strip().split(';') for _ in open(file)):
        if line_count < skip_count:
            line_count += 1
            continue
        yield e


def read_all_runs(input_dir):
    data = []
    for file_name in file_name_header_sizes.keys():
        file = os.path.join(input_dir, file_name + '.txt')
        skip_count = file_name_header_sizes[file_name]
        for e in skip_lines_file(file, skip_count):
            data.append((float(e[0]), file_name, '\t'.join(e[1:])))
    return sorted(data, key=itemgetter(0,1))


def main(args):
    input_dir, output_dir = args[:2]
    for run_name, dir in get_input_directories(input_dir):
        print 'Reading in', run_name
        w = open(os.path.join(output_dir, run_name + '.txt'), 'w')
        for timestamp, file_name, data in read_all_runs(dir):
            w.write('%s\t%s\t%s\n' % (timestamp, file_name, data))
        w.close()


if __name__ == '__main__':
    main(sys.argv[1:])