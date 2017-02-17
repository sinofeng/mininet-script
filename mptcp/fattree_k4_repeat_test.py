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
import sys
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

def throughput_test(net, out_dir='test',test_index = 1, sublflow_num=1, test_type='mptcp', data_step_time=1, connection_interval_time=5, connection_during_time=60,
                    client_hosts = [], server_hosts = []):
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


    # 2. start servers, set output file
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_file_path = "%s/%d_subflows_%s_serverdata_%d.csv" % (out_dir, sublflow_num, test_type, test_index)
    print("Data collection interval time: %f" % data_step_time)
    for host in client_hosts:
        host.cmd('killall iperf')
    for server in server_hosts:
        server.cmd("iperf -s -i %f -y C >> %s &" % (data_step_time, out_file_path))
    # 3. start clients one by one, 5s internal time, lasting for 30s
    host_num = len(client_hosts)
    for i in range(0, host_num):
        client_hosts[i].cmd("iperf -c %s -t%d &" % (server_hosts[i].IP(), connection_during_time))
        sleep(connection_interval_time)
    # 4. analyze output file, generate  aggregateData file
    # csv_reader = csv.reader(open(out_fiile_path , encoding='utf-8'))
    # for row in csv_reader:
    #     print row
    # 5. generate result file.
    remain_time = connection_during_time
    countDown('Waiting all connection finished, remain time: %ds....', remain_time)
    print 'A sub-test complete.'
    return out_file_path


def readTestFlag():
    input = raw_input("Enter (y) to start test, or not:")
    if input == 'y':
        return True
    else:
        return False

def readTestType():
    input = raw_input("Enter num to select test type, 0.Random-based ECMP; 1.MPTCP-awared loadbalance(DEFAULT) :")
    type_code = int(input)
    test_type = '';
    if type_code == 0:
        test_type = 'ecmp'
    else:
        test_type = 'mptcp'
    return test_type

def readStartSubflowNum():
    input = raw_input("Enter start num of subflows:")
    return int(input)

def readEndSubflowNum():
    input = raw_input("Enter end num of subflows:")
    return int(input)

def readConnectionInterval():
    input = raw_input("Enter connection interval time:")
    return int(input)

def readConnectionDuringTime():
    input = raw_input("Enter connection during time:")
    return int(input)

def readFatTreeK():
    input = raw_input("Enter k value of the FatTree:")
    return int(input)

def readTestName():
    input = raw_input("Enter test name:")
    return input

def countDown(format_str='Remain time %d', remain_time=30):
    while True:
        print('\r' + format_str % remain_time),
        sys.stdout.flush()
        remain_time -= 1
        sleep(1)
        if remain_time == 0:
            break
def readTestRepeatTimes():
    input = raw_input("Enter test repeat times:")
    return int(input)

def main():
    '''
    1. Radomly selcect hosts and servers.
    2. Repeat throughput test use fixed hosts.
    :return:
    '''

    # 1. declare and parse arguments
    top_dir = os.path.join("result")
    if not os.path.exists(top_dir):
        os.makedirs(top_dir)
    subflow_num_start = 1
    subflow_num_end = 9
    test_name = 'test1'
    test_type = 'mptcp'  # 0: random-based ecmp; 1:mptcp-awared load-balance
    #datacollection_step_time = 1
    connection_interval_time = 5
    connection_during_time = 30
    # 2. createTopo
    k_value = readFatTreeK()
    topo = FatTreeTopo(k=k_value)
    # link = custom(TCLink, bw=10)  # , delay=args.delay)
    link = custom(TCLink, bw=10)  # , delay=args.delay)
    c0 = RemoteController(name='c0', ip='10.103.89.185',port=6633)
    #c0 = RemoteController(name='c0', ip='10.103.90.184', port=6633)
    net = Mininet(controller=c0, topo=topo,
                  link=TCLink, switch=OVSKernelSwitch)
    # c0 = net.addController('c0', ip='10.103.89.185', port=6633)
    net.start()
    countDown('Pepareing for test, remain time:%d....', 10)
    # net.pingAll()

    hosts = list(net.hosts)
    host_0 = hosts[0]
    for host in hosts:
        net.ping([host_0, host])
    host_count = len(hosts)

    # 3. start evaluation
    while True:
        test_flag = readTestFlag()
        if test_flag == False:
            break
        test_name = readTestName()
        test_dir = os.path.join(top_dir, test_name)
        test_type = readTestType()
        subflow_num_start = readStartSubflowNum()
        subflow_num_end = readEndSubflowNum()
        connection_interval_time = readConnectionInterval()
        connection_during_time = readConnectionDuringTime()
        test_info = "Test info,Test type:%s, Subflow num:%d--%d, Connection interval: %d, Connection during: %d" % (test_type, subflow_num_start, subflow_num_end, connection_interval_time, connection_during_time)
        print test_info
        test_time = (len(net.hosts) - 1) * connection_interval_time + connection_during_time
        print('Test time: %d' % test_time)
        os.popen("sudo touch README.md" )
        os.popen("sudo echo %s >> README.md" % test_info)
        print 'Start test ...'
        testepeatTimes =  readTestRepeatTimes()
        for test_index in range(1, testepeatTimes + 1):
            client_hosts, server_hosts = selectHostsPairs(hosts)
            # random.shuffle(client_hosts)
            # c_hosts = client_hosts[0:host_count / 2]
            c_hosts = client_hosts
            # s_hosts = client_hosts[host_count / 2: host_count]
            s_hosts = server_hosts
            for subflow_num in range(subflow_num_start, subflow_num_end + 1):
                print 'Sub-test start,subflow num: %d.....' % subflow_num
                cmd_set_subflw = "echo '" + str(subflow_num) + "' > /sys/module/mptcp_fullmesh/parameters/num_subflows"
                os.popen(cmd_set_subflw)
                throughput_test(net, test_dir, test_index, subflow_num, test_type, 1, connection_interval_time,
                                connection_during_time,
                                c_hosts, s_hosts)
    CLI(net)

    net.stop()



if __name__ == '__main__':
    setLogLevel('debug')
    main()