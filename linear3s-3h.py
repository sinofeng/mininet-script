#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def createTopo():

    net = Mininet(build= False);

    s1 = net.addSwitch('s1');
    s2 = net.addSwitch('s2');
    s3 = net.addSwitch('s3');

    net.addLink(s1, s2)
    net.addLink(s1, s3)

    net.start()

    s1.cmd('ifconfig s1 inet 192.168.0.1/24')
    s2.cmd('ifconfig s2 inet 192.168.0.2/24')
    s3.cmd('ifconfig s3 inet 192.168.0.3/24')

    CLI(net)

    net.stop()


if __name__=='__main__':
    setLogLevel('debug')
    createTopo()