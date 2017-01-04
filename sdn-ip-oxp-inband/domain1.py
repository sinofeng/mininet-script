#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info, debug, error
from mininet.node import Host, RemoteController, OVSSwitch
from mininet.util import quietRun
from mininet.link import Intf
import re

QUAGGA_DIR = '/usr/lib/quagga'
# Must exist and be owned by quagga user (quagga:quagga by default on Ubuntu)
QUAGGA_RUN_DIR = '/var/run/quagga'
CONFIG_DIR = 'config'


class InbandController(RemoteController):
    "Controller running in in-band control way."

    # def checkListening(self):
    #     "Overidden to do nothing, avoid error because of ip&port check. "
    #     return
    def isListening(self, ip, port):
        return True

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

class RootHost(Host):
    def __init__(self, name, intfDict, route, *args, **kwargs):
        Host.__init__(self, name,inNamespace=False , *args, **kwargs)
        self.intfDict = intfDict
        self.route = route

    def config(self, **kwargs):
        Host.config(self, **kwargs)
        for intf, attrs in self.intfDict.items():
            self.cmd('ip addr flush dev %s' % intf)
            if 'mac' in attrs:
                self.cmd('ip link set %s down' % intf)
                self.cmd('ip link set %s address %s' % (intf, attrs['mac']))
                self.cmd('ip link set %s up ' % intf)
            for addr in attrs['ipAddrs']:
                self.cmd('ip addr add %s dev %s' % (addr, intf))
        self.cmd('route del default ')
        self.cmd('route del -net 10.103.89.0/24 ')
        self.cmd('route add -net 10.103.0.0/16 dev ens160')
        self.cmd('route add -net 10.103.0.0/16 gw 10.103.89.1')
        self.cmd('ip route add default via %s' % self.route)
        # set route
        #self.cmd("ip route add 10.0.2.0/30 via %s" % self.route)

class SdnIpTopo( Topo ):

    def build(self):


        s1 = self.addSwitch('s1', dpid='0000000000000011',switch=OVSSwitch , inband=True)
        s2 = self.addSwitch('s2', dpid='0000000000000012', switch=OVSSwitch  ,inband=True)

        zebraConf = '%s/zebra.conf' % CONFIG_DIR

        bgpEth0 = {'mac': '00:00:00:00:00:02',
                   'ipAddrs': ['10.10.11.1/24']}
        bgpEth1 = {'ipAddrs': ['10.10.10.1/24']}

        bgpIntfs = {'bgp-eth0': bgpEth0,
                    'bgp-eth1': bgpEth1}

        bgp = self.addHost("bgp", cls=Router,
                           quaggaConfFile='%s/quagga-sdn1.conf' % CONFIG_DIR,
                           zebraConfFile=zebraConf,
                           intfDict=bgpIntfs)

        self.addLink(bgp, s1)

        rootEth0 = {'ipAddrs':['10.10.10.2/24']}
        rootEth1 = {'ipAddrs':['10.0.2.1/30']}
        rootEth2 = {'ipAddrs':['10.10.21.1/24']}
        rootHostIntfs = {'root-eth0': rootEth0,
                         'root-eth1': rootEth1,
                         'root-eth2': rootEth2}
        root = self.addHost('root', cls=RootHost, intfDict=rootHostIntfs, route='10.0.2.2')

        self.addLink(bgp, root)
        self.addLink(s1, s2)

        h1 = self.addHost('h1', ip='192.168.1.1/16')
        h2 = self.addHost('h2', ip='192.168.1.2/16')

        self.addLink(s1, h1)
        self.addLink(s2, h2)
        self.addLink(s1, root)
        self.addLink(s1, root)






topos = {'SdnIpTopo': SdnIpTopo}

if __name__ =='__main__':
    setLogLevel('debug')
    topo = SdnIpTopo()
    net = Mininet(topo=topo, controller=InbandController)



    intfName = "ens224"
    _intf = Intf(intfName, net.getNodeByName('s2'))
    s1 = net.getNodeByName('s1')
    s2 = net.getNodeByName('s2')


    net.start()

    c1 = net.addController('c1', ip="10.10.21.1", port=6633)

    #net.build()

    c1.start()

    s1.start([c1])
    s2.start([c1])

    s1.cmd("ovs-vsctl set bridge s1 stp-enable=true")
    s2.cmd("ovs-vsctl set bridge s2 stp-enable=true")

    s1.cmd("ifconfig s1 inet 10.10.21.11/24")
    s2.cmd("ifconfig s2 inet 10.10.21.12/24")

    #net.getNodeByName('root').cmd('ip route add 10.0.2.1/30 10.0.2.3')



    CLI(net)

    net.stop()