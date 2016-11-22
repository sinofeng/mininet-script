#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info, error
from mininet.util import quietRun
from mininet.link import Intf
import re

class InbandController(RemoteController):
    "Controller running in in-band control way."

    def checkListening(self):
        "Overidden to do nothing, avoid error because of ip&port check. "
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

def createInboundNet():

    net = Mininet(topo=None,
                  build=False,
                  switch=OVSSwitch,
                  controller=InbandController)

    c0 = net.addController('c0', ip="10.10.100.1", port=6633) # set remote controller ip & port

    # add 3 hosts to network. controller software will run on h1
    h1 = net.addHost('h1', ip='192.168.0.1/24')

    # add switch, enable in-band control
    s1 = net.addSwitch('s1', inband=True)

    # add links
    net.addLink(h1, s1)

    # add interface
    intf1CtrName = "ens192"
    intf2CtrName = "ens224"
    _intf1Ctr = Intf(intf1CtrName, node=s1)
    _intf2Ctr = Intf(intf2CtrName, node=s1)

    net.start()

    # s1 need to be equipped with an ip address to contact the controller
    s1.cmd('ifconfig s1 inet 10.10.100.2/24')

    # run controller sofware on h1, and redirect STDOUT & STDERR to log file
    # h1.cmd("ovs-testcontroller ptcp:6633 1>/tmp/c0.log 2>/tmp/c0.log &")

    CLI(net)
    net.stop()

if __name__=='__main__':
    setLogLevel('debug')
    createInboundNet()