#!/usr/bin/python

import os
import csv
import matplotlib.pyplot as plt
if __name__ == '__main__':
    # 1. input result dir path
    top_dir = raw_input("Enter data dir path:")
    # top_dir = 'result/test16'
    bw_result_file_path = os.path.join(top_dir, 'average_ratio_result.csv')
    stdev_result_file_path = os.path.join(top_dir, 'stdev_result.csv')
    # 2. read bw
    subflow_nums = []
    mptcp_bw_ratios = []
    ecmp_bw_ratios = []
    with open(bw_result_file_path) as bw_ratio_file:
        bw_ratio_reader = csv.reader(bw_ratio_file)
        subflow_nums = bw_ratio_reader.next()
        mptcp_bw_ratios = bw_ratio_reader.next()
        ecmp_bw_ratios = bw_ratio_reader.next()
    # 3. read stdev
    mptcp_stdevs = []
    ecmp_stdevs = []
    with open(stdev_result_file_path) as bw_ratio_file:
        bw_ratio_reader = csv.reader(bw_ratio_file)
        bw_ratio_reader.next()
        mptcp_stdevs = bw_ratio_reader.next()
        ecmp_stdevs = bw_ratio_reader.next()
    # 4. plot and show
    fig = plt.figure()
    fig.suptitle('Result')
    bw_fig = fig.add_subplot(121)
    bw_fig.set_title('Average bandwidth ratio in random traffic')
    bw_fig.set_xlabel('MPTCP subflow num')
    bw_fig.set_ylabel('Average bandwidth ratio')
    bw_fig.plot(subflow_nums, mptcp_bw_ratios, 'ro-', label='MPTCP-awared Load Balancer')
    bw_fig.plot(subflow_nums, ecmp_bw_ratios, 'b^-', label='Hash-based ECMP')
    bw_fig.legend(loc=4)

    stdev_fig = fig.add_subplot(122)
    stdev_fig.set_title('Load jitter in random traffic')
    stdev_fig.set_xlabel('MPTCP subflow num')
    stdev_fig.set_ylabel('Load jitter')
    stdev_fig.plot(subflow_nums, mptcp_stdevs, 'ro-', label='MPTCP-awared Load Balancer')
    stdev_fig.plot(subflow_nums, ecmp_stdevs,  'b^-', label='Hash-based ECMP')
    stdev_fig.legend()

    plt.show()
    pass