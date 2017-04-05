#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info, debug, error
from mininet.node import Host, RemoteController
from mininet.util import quietRun
from mininet.link import Intf
import re

QUAGGA_DIR = '/usr/lib/quagga'
# Must exist and be owned by quagga user (quagga:quagga by default on Ubuntu)
QUAGGA_RUN_DIR = '/var/run/quagga'
CONFIG_DIR = 'config'

class SdnIpHost(Host):
    def __init__(self, name, ip, route, *args, **kwargs):
        Host.__init__(self, name, ip=ip, *args, **kwargs)

        self.route = route

    def config(self, **kwargs):
        Host.config(self, **kwargs)

        debug("configuring route %s" % self.route)

        self.cmd('ip route add default via %s' % self.route)

class Router(Host):
    def __init__(self, name, quaggaConfFile, zebraConfFile, intfDict, *args, **kwargs):
        Host.__init__(self, name, *args, **kwargs)

        self.quaggaConfFile = quaggaConfFile
        self.zebraConfFile = zebraConfFile
        self.intfDict = intfDict

    def config(self, **kwargs):
        Host.config(self, **kwargs)
        self.cmd('sysctl net.ipv4.ip_forward=1')

        for intf, attrs in self.intfDict.items():
            self.cmd('ip addr flush dev %s' % intf)
            if 'mac' in attrs:
                self.cmd('ip link set %s down' % intf)
                self.cmd('ip link set %s address %s' % (intf, attrs['mac']))
                self.cmd('ip link set %s up ' % intf)
            for addr in attrs['ipAddrs']:
                self.cmd('ip addr add %s dev %s' % (addr, intf))

        self.cmd('/usr/lib/quagga/zebra -d -f %s -z %s/zebra%s.api -i %s/zebra%s.pid' % (self.zebraConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))
        self.cmd('/usr/lib/quagga/bgpd -d -f %s -z %s/zebra%s.api -i %s/bgpd%s.pid' % (self.quaggaConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))


    def terminate(self):
        self.cmd("ps ax | egrep 'bgpd%s.pid|zebra%s.pid' | awk '{print $1}' | xargs kill" % (self.name, self.name))

        Host.terminate(self)


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


class SdnIpTopo( Topo ):
    "SDN-IP As3 topology"

    def build(self):
        s3 = self.addSwitch('s3', dpid='0000000000000021')
        s4 = self.addSwitch('s4', dpid='0000000000000022')

        zebraConf = '%s/zebra.conf' % CONFIG_DIR

        bgpEth0 = {'mac': '00:00:00:00:00:02',
                   'ipAddrs': ['10.0.1.1/24']}
        bgpEth1 = {'ipAddrs': ['10.10.12.1/24']}
        bgpIntfs = {'bgp-eth0': bgpEth0,
                    'bgp-eth1': bgpEth1}

        bgp = self.addHost("bgp", cls=Router,
                           quaggaConfFile='%s/quagga-sdn2.conf' % CONFIG_DIR,
                           zebraConfFile=zebraConf,
                           intfDict=bgpIntfs)

        self.addLink( bgp, s3 )

        # Connect BGP speaker to the root namespace so it can peer with ONOS
        root = self.addHost('root', inNamespace=False, ip='10.10.12.2/24')

        self.addLink(root, bgp)

        self.addLink( s3, s4 )

        h1 = self.addHost('h1', cls=SdnIpHost, ip='192.168.2.1/24', route='192.168.2.254')
        h2 = self.addHost('h2', cls=SdnIpHost, ip='192.168.2.2/24', route='192.168.2.254')

        self.addLink( s3, h1 )
        self.addLink( s4, h2 )

        # add interface
        # intfName= "ens424"
        # _intf = Intf(intfName, node=s3)

topos = {'sdnip': SdnIpTopo}

if __name__ == '__main__':
    setLogLevel('debug')
    topo = SdnIpTopo()

    net = Mininet(topo=topo, controller=RemoteController)

    intfName = "ens192"
    _intf = Intf(intfName, net.getNodeByName('s4'))

    net.start()

    CLI(net)

    net.stop()

    info("done\n")



