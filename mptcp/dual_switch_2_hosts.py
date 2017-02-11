#!/usr/bin/python

""" Script to use MPTCP in Mininet. Run on commandline as, python singleswitch-mptcp.py
    # auto done, no need to do it {Start the switch s1 in mininet, "switch s1 start" command.
    (add flows in s1 by :ovs-ofctl add-flow s1 in_port=1,actions=output:3 or drop ...and so on)}
    check the iperf for multipath connection (MPTCP) gained throughput over two links!!!
    links could be set down : link s1 h2 down
    or simply by droping the returning packets
 """

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink

def topology():
    "Create a network."
  # Defining network
    net = Mininet( controller=RemoteController, link=TCLink, switch=OVSKernelSwitch )
    print "*** Creating nodes"
  # Adding hosts, switches and controller
    h1 = net.addHost( 'h1', mac='00:00:00:00:00:01', ip='10.0.0.1/24' )
    h2 = net.addHost( 'h2', mac='00:00:00:00:00:02', ip='10.0.0.2/24' )
    s1 = net.addSwitch( 's1' )
    s2 = net.addSwitch( 's2' )
    #s2 = net.addSwitch( 's2' )
    #c0 = net.addController( 'c0', controller=RemoteController, ip='127.0.0.1', port=6653 )
    
    print "*** Creating links"  
  # Adding links and link bandwidth
    net.addLink(h1, s1, intfName1='h1-eth0', intfName2='s1-eth1', bw=10)
    net.addLink(h1, s1, intfName1='h1-eth1', intfName2='s1-eth2', bw=10)

    net.addLink(h2, s2, intfName1='h2-eth0', intfName2='s2-eth1', bw=10)
    net.addLink(h2, s2, intfName1='h2-eth1', intfName2='s2-eth2', bw=10)

    net.addLink(s1, s2, intfName1='s1-eth3', intfName2='s2-eth3', bw=10)
    net.addLink(s1, s2, intfName1='s1-eth4', intfName2='s2-eth4', bw=10)

  # Commands for identifyig the second interfaces of h1 and h2 hosts
    h1.cmd('ifconfig h1-eth1 10.0.10.1 netmask 255.255.255.0')
    h2.cmd('ifconfig h2-eth1 10.0.10.2 netmask 255.255.255.0')

    print "*** Starting network"
    net.build()

    c0 = net.addController('c0',ip='10.103.89.185', port=6633)
   # start s1 switch
    s1.start([c0])
    s2.start([c0])
   # s1.cmd('switch s1 start')
   # # add flows in switch
   #  s1.cmd('ovs-ofctl add-flow s1 in_port=1,actions:output=3')
   #  s1.cmd('ovs-ofctl add-flow s1 in_port=2,actions:output=4')
   #  s1.cmd('ovs-ofctl add-flow s1 in_port=3,actions:output=1')
   #  s1.cmd('ovs-ofctl add-flow s1 in_port=4,actions:output=2')
   #
   #  s1.cmd('ovs-ofctl add-flow s2 in_port=1,actions:output=3')
   #  s1.cmd('ovs-ofctl add-flow s2 in_port=2,actions:output=4')
   #  s1.cmd('ovs-ofctl add-flow s2 in_port=3,actions:output=1')
   #  s1.cmd('ovs-ofctl add-flow s2 in_port=4,actions:output=2')


    print "*** Running CLI"
    CLI( net )

    print "*** Stopping network"

    net.stop()

if __name__ == '__main__':

    setLogLevel( 'debug' )

    topology()