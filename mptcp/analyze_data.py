#!/usr/bin/python

import os
import csv


if __name__ == '__main__':
    # 1. get ips-->bw
    # 2. leverage bw

    bw_map = {}
    bw_ration_map = None
    bw_average = 0
    bw_optimal = 10000
    bw__average_ratio = 0.0
    num_sublflow = 2
    csv_reader = csv.reader(open('result/test1/1_4_serverdata.csv'))
    for row in csv_reader:
        src_ip = row[1]
        dst_ip = row[3]
        time_interval = row[6].split('-')
        start_time = float(time_interval[0])
        end_time = float(time_interval[1])
        if start_time == 0 and end_time <=2:
            continue
        if start_time > 0:
            continue
        bw = int(row[8])
        bw_map[(src_ip, dst_ip)] = bw
    bw_sum = 0
    con_num = 0;
    for bw in bw_map.values():
        bw_sum += bw
        con_num +=1
    bw_average = bw_sum / con_num
    bw__average_ratio = bw_average / bw_optimal
    print('Average bw:%d, Optimal bw:%d,  Average bw ratio: %d' % (bw_average, bw_optimal, bw__average_ratio))
    pass