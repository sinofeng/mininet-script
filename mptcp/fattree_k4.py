#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink
from dctopo import FatTreeTopo
from mininet.util import dumpNodeConnections, custom
import random
import os
from time import sleep, time
import csv
from subprocess import call


def selectHostsPairs(hosts):
    n = len(hosts)
    clients = []
    servers = []
    servers_index = []
    for i in range(0,n):
        clients.append(hosts[i])
        servers_index.append(i)
    while True:
        random.shuffle(servers_index)
        flag = True
        for i in range(0,n):
            if i == servers_index[i]:
                flag = False
        if flag:
            break
    for i in range(0,n):
        servers.append(hosts[servers_index[i]])
    return  clients, servers

def throughput_test(net,out_dir='test',test_index=1, sublflow_num=1, test_type='mptcp'):
    """
    :param:net
    :param: out_dir
    :param:test_index
    :param: subflow_num
    :return:
    """
    """
    File-name format:
    1.iperf server output file:
      ${test_index}_${subflow_num}_${test_type}_${serverdata}.csv
      file content:
      transferID,srcip,dstip,srcport,dstport,unkhown,start-endtime,transfered_bytes,bits_per_second
    3.aggregate data file after a test:
      ${test_index}_${subflow_num}_${aggregate}.csv
    4.result file
      ${test_index}_${subflow_num}_${result}.txt
      file content:
      test_name=${test_name}
      test_index=${test_index}
      subflow_num=${subflow_num}
      optimal_throughput_value=${optimal_throughput_value}
      average_throughput_value=${average_throughput_value}
      average_throughput=${average_throughput}
    """
    # 1. randomly select N pairs hosts, N is the num of hosts
    hosts = list(net.hosts)
    N = len(hosts)
    client_hosts, server_hosts = selectHostsPairs(hosts)

    # 2. start servers, set output file
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_fiile_path = "%s/%d_%d_%s_serverdata.csv" % (out_dir, test_index, sublflow_num, test_type)
    for server in server_hosts:
        server.cmd("iperf -s -i2 -y C >> %s &" % out_fiile_path)
    # 3. start clients one by one, 5s internal time, lasting for 30s
    host_num = len(client_hosts)
    for i in range(0, 2):
        client_hosts[i].cmd("iperf -c %s -t30 &" % server_hosts[i].IP())
        sleep(5)
    # 4. analyze output file, generate  aggregateData file
    # csv_reader = csv.reader(open(out_fiile_path , encoding='utf-8'))
    # for row in csv_reader:
    #     print row
    # 5. generate result file.
    return out_fiile_path


def readInput():
    input = raw_input("Enter (y) to start test, or not:")
    if input == 'y':
        return True
    else:
        return False


def main():

    # 1. parseArgument
    top_dir = os.path.join("result")
    if not os.path.exists(top_dir):
        os.makedirs(top_dir)
    num_subflows = 2
    cmd_set_subflw = "echo '" + str(num_subflows) + "' > /sys/module/mptcp_fullmesh/parameters/num_subflows"
    print cmd_set_subflw
    test_type= 1 # 0: random-based ecmp; 1:mptcp-awared load-balance
    #call(cmd_set_subflw)
    os.popen(cmd_set_subflw)
    # 2. createTopo

    topo = FatTreeTopo(k=4)
    link = custom(TCLink, bw=10)  # , delay=args.delay)
    c0 = RemoteController(name='c0', ip='10.103.89.185',port=6633)
    #c0 = RemoteController(name='c0', ip='10.103.90.184', port=6633)
    net = Mininet(controller=c0, topo=topo,
                  link=link, switch=OVSKernelSwitch)
    # c0 = net.addController('c0', ip='10.103.89.185', port=6633)
    net.start()
    # 3. start evaluation

    test_flag = False
    while True:
        test_flag = readInput()
        if test_flag == False:
            break
            print 'Start test ...'
        test_dir = os.path.join(top_dir, "test1")
        throughput_test(net, test_dir, 1, 2)

    CLI(net)

    net.stop()



if __name__ == '__main__':
    setLogLevel('debug')
    main()