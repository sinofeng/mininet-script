#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info


class InbandController(RemoteController):
    "Controller running in in-band control way."

    def checkListening(self):
        "Overidden to do nothing, avoid error because of ip&port check. "
        return

def createInboundNet():

    net = Mininet(topo=None,
                  build=False,
                  switch=OVSSwitch,
                  controller=InbandController)

    c0 = net.addController('c0', ip="192.168.1.1", port=6633) # set remote controller ip & port

    # add 3 hosts to network. controller software will run on h1
    h1 = net.addHost('h1', ip='192.168.1.1/24')
    h2 = net.addHost('h2', ip='192.168.0.2/24')
    h3 = net.addHost('h3', ip='192.168.0.3/24')

    # add switch, enable in-band control
    s1 = net.addSwitch('s1', inband=True)
    s2 = net.addSwitch('s2', inband=True)
    s3 = net.addSwitch('s3', inband=True)
    s4 = net.addSwitch('s4', inband=True)

    switchList = (s1, s2, s3, s4)

    # add links
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(h3, s3)

    for i in range(0, len(switchList)):
        for j in range(i+1, len(switchList)):
            net.addLink(switchList[i], switchList[j])

    net.start()

    s1.cmd("ovs-vsctl set bridge s1 stp-enable=true")
    s2.cmd("ovs-vsctl set bridge s2 stp-enable=true")
    s3.cmd("ovs-vsctl set bridge s3 stp-enable=true")
    s4.cmd("ovs-vsctl set bridge s4 stp-enable=true")

    # s1 need to be equipped with an ip address to contact the controller
    s1.cmd('ifconfig s1 inet 192.168.1.11/24')
    s2.cmd('ifconfig s2 inet 192.168.1.12/24')
    s3.cmd('ifconfig s3 inet 192.168.1.13/24')
    s4.cmd('ifconfig s4 inet 192.168.1.14/24')

    # run controller sofware on h1, and redirect STDOUT & STDERR to log file
    h1.cmd("ovs-testcontroller ptcp:6633 1>/tmp/c0.log 2>/tmp/c0.log &")

    CLI(net)
    net.stop()

if __name__=='__main__':
    setLogLevel('debug')
    createInboundNet()