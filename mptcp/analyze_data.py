#!/usr/bin/python

import os
import csv
import sys, getopt
import pydevd

def analyze_single_file_throughput(filepath):
    '''
    Analyze single file throughput.
    :param filepath:
    :return: {'testType':'mptcp', 'subflowNum': 1, 'averageBw':10000000}
    '''
    pass

if __name__ == '__main__':
    # debug:
    # pydevd.settrace('10.103.90.184', port=5151, stdoutToServer=True, stderrToServer=True)
    input_file_path = ' ';
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:")
    except getopt.GetoptError:
        print "analyze_data.py -i <inputfile>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print "analyze_data.py -i <inputfile>"
            sys.exit()
        elif opt == '-i':
            input_file_path = arg
    # 1. get ips-->bw
    # 2. leverage bw

    bw_map = {}
    bw_ration_map = None
    bw_average = 0.0
    bw_optimal = 10000000.0
    bw__average_ratio = 0.0
    num_sublflow = 2
    standard_deviation = 0.0
    csv_reader = csv.reader(open(input_file_path))
    count = 0;
    for row in csv_reader:
        src_ip = row[1]
        dst_ip = row[3]
        time_interval = row[6].split('-')
        start_time = float(time_interval[0])
        end_time = float(time_interval[1])
        count += 1
        if start_time == 0 and end_time <=2:
            continue
        if start_time > 0:
            continue
        bw = float(row[8])
        bw_map[(src_ip, dst_ip)] = bw
    print("Data lines:%d" % count)
    bw_sum = 0.0
    con_num = 0.0;
    for bw in bw_map.values():
        bw_sum += bw
        con_num +=1
    bw_average = bw_sum / con_num
    bw__average_ratio = bw_average / bw_optimal
    print('Average bw:%d, Optimal bw:%d,  Average bw ratio: %f' % (bw_average, bw_optimal, bw__average_ratio))
    pass