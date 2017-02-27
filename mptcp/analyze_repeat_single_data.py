#!/usr/bin/python

import os
import csv
import sys, getopt
import pydevd
import string
import matplotlib.pyplot as plt
import pydevd
import cmath

def analyze_single_file_throughput(file_path):
    '''
    Analyze single file throughput.
    :param file_path:
    :return: {'testType':'mptcp', 'subflowNum': 1, 'averageBw':10000000, "stdevList": [{"time":1, "stdev":0.918}]}
    '''
    #file_path = ' ';
    # 1. get ips-->bw
    # 2. leverage bw
    result = {"sumBwDict":{}}
    bw_map = {}
    stdevDict = {}
    bw_ration_map = None
    bw_average = 0.0
    bw_optimal = 10000000.0
    bw__average_ratio = 0.0
    num_sublflow = 2
    standard_deviation = 0.0
    csv_reader = csv.reader(open(file_path))
    count = 0;
    absolute_start_time = 0
    for row in csv_reader:
        time = int(row[0])
        src_ip = row[1]
        dst_ip = row[3]
        time_interval = row[6].split('-')
        start_time = float(time_interval[0])
        end_time = float(time_interval[1])
        count += 1
        # throughput
        bw = float(row[8])
        if absolute_start_time == 0:
            absolute_start_time = time
        relative_time = time - absolute_start_time
        if (end_time - start_time) == 1:
            if relative_time not in stdevDict:
                stdevDict[relative_time] = []
            stdevDict[relative_time].append({"ips": (src_ip, dst_ip), "bw": bw})
        if start_time == 0 and end_time <= 2:
            continue
        if start_time > 0:
            continue
        bw_map[(src_ip, dst_ip)] = bw

    print("Data lines:%d" % count)
    bw_sum = 0.0
    con_num = 0.0;
    for bw in bw_map.values():
        bw_sum += bw
        con_num += 1
    bw_average = bw_sum / con_num
    bw__average_ratio = bw_average / bw_optimal
    print('Average bw:%d, Optimal bw:%d,  Average bw ratio: %f' % (bw_average, bw_optimal, bw__average_ratio))

    # handle stdev
    max_bw_sum = 0.0
    for time in stdevDict.keys():
        dataList = stdevDict[time]
        stdev = 1.0
        bw_sum = 0.0
        bw_ave = 0.0
        count = 0
        for data in dataList:
            bw_sum += data["bw"]
            count += 1
        # bw_ave = bw_sum/count
        # tmp = 0.0
        # for data in dataList:
        #     tmp +=(data["bw"] - bw_ave)**2
        # stdev = cmath.sqrt(tmp/count)
        if bw_sum > max_bw_sum:
            max_bw_sum = bw_sum

    stdev_sum = 0.0
    for bw in bw_map.values():
        stdev_sum = (bw/1000000 - bw_average/1000000)**2
    # stdev = float(cmath.sqrt(stdev_sum/con_num))
    stdev = (stdev_sum/con_num) ** 0.5
    result['maxThroughput']= max_bw_sum
    result['averageBw'] = bw_average
    result['averageBwRatio'] = bw__average_ratio
    result['stdev'] = stdev
    print result
    return result
    pass

if __name__ == '__main__':
    # debug:
    # pydevd.settrace('10.103.90.184', port=5151, stdoutToServer=True, stderrToServer=True)
    # 1. read data dir
    # top_dir = raw_input("Enter data dir path:")
    top_dir = 'result/test16'
    # 2. ls files and seperate file by test type
    files = os.listdir(top_dir)
    mptcp_src_files = []
    ecmp_src_files = []
    test_index = int(raw_input("Enter text index:"))
    for file in files:
        if string.find(file, 'result') != -1:
            continue
        index = int(string.split(string.split(file, '_')[4], '.')[0])
        if index != test_index:
            continue
        if string.find(file, 'mptcp') != -1:
            mptcp_src_files.append(file)
        elif string.find(file, 'ecmp') != -1:
            ecmp_src_files.append(file)
        else:
            continue
    # 3. call analyze_single_file_throughput() handle all files
    #   mptcp_list[{}], ecmp_list[{}], order thhese list
    mptcp_result_list = []
    ecmp_result_list = []
    for file_name in mptcp_src_files:
        args = string.split(file_name, '_')
        subflow_num = int(args[0])
        result_data = analyze_single_file_throughput(os.path.join(top_dir, file_name))
        result_data['testType'] = 'mptcp'
        result_data['subflowNum'] = subflow_num
        mptcp_result_list.append(result_data)
    for file_name in ecmp_src_files:
        args = string.split(file_name, '_')
        subflow_num = int(args[0])
        result_data = analyze_single_file_throughput(os.path.join(top_dir, file_name))
        result_data['testType'] = 'ecmp'
        result_data['subflowNum'] = subflow_num
        ecmp_result_list.append(result_data)
    mptcp_result_list.sort(key = lambda k : (k.get('subflowNum')))
    ecmp_result_list.sort(key = lambda k : (k.get('subflowNum')))
    # 4. Output analyzed Data and plot
    mptcp_show_subflownum = []
    mptcp_show_bwratio = []
    mptcp_show_maxthroughput = []
    mptcp_show_stdev = []
    ecmp_show_subflownum = []
    ecmp_show_bwratio = []
    ecmp_show_maxthroughput = []
    ecmp_show_stdev = []
    for data in mptcp_result_list:
        mptcp_show_subflownum.append(data['subflowNum'])
        mptcp_show_bwratio.append(data['averageBwRatio'])
        mptcp_show_maxthroughput.append(data['maxThroughput'])
        mptcp_show_stdev.append(data['stdev'])
    for data in ecmp_result_list:
        ecmp_show_subflownum.append(data['subflowNum'])
        ecmp_show_bwratio.append(data['averageBwRatio'])
        ecmp_show_maxthroughput.append(data['maxThroughput'])
        ecmp_show_stdev.append(data['stdev'])
    plt.subplot(131)
    plt.plot(mptcp_show_subflownum,mptcp_show_bwratio, 'r-', ecmp_show_subflownum, ecmp_show_bwratio, 'b-')
    plt.subplot(132)
    plt.plot(mptcp_show_subflownum, mptcp_show_maxthroughput, 'r-', ecmp_show_subflownum, ecmp_show_maxthroughput, 'b-')
    plt.subplot(133)
    plt.plot(mptcp_show_subflownum, mptcp_show_stdev, 'r-', ecmp_show_subflownum, ecmp_show_stdev, 'b-')
    plt.show()
    plt
    pass