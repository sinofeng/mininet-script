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
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import Intf

class InbandController(RemoteController):

    def checkListening(self):
        "Overidden to do nothing"
        return

def checkIntf( intf ):
    "Make sure intf exists and is not configured."
    config = quietRun( 'ifconfig %s 2>/dev/null' % intf, shell=True )
    if not config:
        error( 'Error:', intf, 'does not exist!\n' )
        exit( 1 )
    ips = re.findall( r'\d+\.\d+\.\d+\.\d+', config )
    if ips:
        error( 'Error:', intf, 'has an IP address,'
               'and is probably in use!\n' )
        exit( 1 )

def multiControllerNet():
    "Create a network from semi-scratch with multiple controllers."

    net = Mininet( controller=InbandController, switch=OVSSwitch )

    print( "*** Creating (reference) controllers" )
    c1 = net.addController( 'c1',ip="192.168.5.1" ,port=6633 )

    print( "*** Creating switches" )
    s1 = net.addSwitch( 's1',inband=True )

    print( "*** Creating hosts" )
    #hosts1 = [ net.addHost( 'h%d' % n ) for n in ( 1, 3 ) ]
    #h1 = net.addHost("h1", ip="192.168.3.1")
    h2 = net.addHost("h3", ip="192.168.4.2")
    h3 = net.addHost("h2", ip="192.168.4.3")

    print( "*** Creating links" )
    #for h in hosts1:
    #    net.addLink( s1, h )
    #net.addLink(s1, h1)
    net.addLink(s1, h2)
    net.addLink(s1, h3)

    intfName ="eth1"
    info( '*** Connecting to hw intf: %s' % intfName )

    info( '*** Adding hardware interface', intfName, 'to switch',
          s1.name, '\n' )
    _intf = Intf( intfName, node=s1 )

    print( "*** Starting network" )
    net.build()
    c1.start()
    s1.start( [ c1 ] )

    print( "*** Testing network" )
    #net.pingAll()
    s1.cmd("ifconfig s1 192.168.5.10")

    print( "*** Running CLI" )
    CLI( net )

    print( "*** Stopping network" )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )  # for CLI output
    multiControllerNet()
