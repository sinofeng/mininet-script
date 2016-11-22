#!/usr/bin/python

"""
This example creates a multi-controller network from semi-scratch by
using the net.add*() API and manually starting the switches and controllers.

This is the "mid-level" API, which is an alternative to the "high-level"
Topo() API which supports parametrized topology classes.

Note that one could also create a custom switch class and pass it into
the Mininet() constructor.
"""


from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch, Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import Intf


def multiControllerNet():
    "Create a network from semi-scratch with multiple controllers."

    net = Mininet(switch=OVSSwitch )

    c0 = Controller("c0")

    print( "*** Creating switches" )
    s1 = net.addSwitch( 's1')

    print( "*** Creating hosts" )
    #hosts1 = [ net.addHost( 'h%d' % n ) for n in ( 1, 3 ) ]
    #h1 = net.addHost("h1", ip="192.168.3.1")
    h11 = net.addHost("h11", ip="192.168.101.1")
    h12 = net.addHost("h12", ip="192.168.102.1")

    print( "*** Creating links" )
    #for h in hosts1:
    #    net.addLink( s1, h )
    #net.addLink(s1, h1)
    net.addLink(s1, h11)
    net.addLink(s1, h12)

    print( "*** Starting network" )
    net.addController(c0)
    net.build()
    c0.start()
    s1.start([c0])

    print( "*** Testing network" )
    #net.pingAll()
    #s1.cmd("ifconfig s1 192.168.5.10")

    print( "*** Running CLI" )
    CLI( net )

    print( "*** Stopping network" )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )  # for CLI output
    multiControllerNet()
