# sdn-ip-oxp-in-band

标签（空格分隔）： oxp sdn-ip in-band

---

##项目描述
  用于OXP组网测试的拓扑，域间普通主机的通信由OXP协议管理，OXP协议中域间Domain控制器和Super控制器连接的建立由SDN-IP负责,并且，控制器与交换机之间以In-Band方式连接。总之：
  SDN-IP + OXP + OF(In-Band)。

###1. 网络拓扑

![网络拓扑图](https://raw.githubusercontent.com/paradisecr/mininet-script/master/sdn-ip-oxp-inband/assets/topo-phy.png)

###2. 网络配置
2.1 网络规划

1. __OF控制平面网络__

OF信道网段:
- Domain1:10.10.21.0/24
- Domain2:10.10.22.0/24

具体地:

|设备 |网络|
|-----|-------|
|domain1控制器|10.10.21.1/24|
|s1|10.10.21.11/24|
|s2|10.10.21.12/24|
|domain2控制器|10.10.22.1/24|
|s3|10.10.22.11/24|
|s4|10.10.22.12/24|

2. __SDN-IP网络__

SDN-IP网络由两部分组成:BGP对等体网络和OF平面网络.其中,BGP对等体网络为OF平面网络通告路由信息,由ONOS的SDN-IP应用负责OF平面网络的通信.

BGP对等体网络:
- eBGP对等体网络: 10.10.11.0/24
- Domain1中的iBGP网络: 10.10.10.0/30
- Domain2中的iBGP网络: 10.10.10.4/30

具体地:

|设备 |网络|
|-----|-------|
|BGP1.eBGP|10.10.11.1/24|
|BGP2.eBGP|10.10.11.2/24|
|BGP1.iBGP|10.10.10.0/30|
|BGP2.iBGP|10.10.10.4/30|

3. OXP网络

|设备 |网络|网关|
|-----|----|---|
|Domain1|10.0.2.1/30|10.0.2.2|
|Domain2|10.0.2.5/30|10.0.2.6|
|Super(与Domain1在同一主机)|10.0.2.1/30|

4. 数据平面网络

数据平面网段:
- Domain1: 192.168.1.0/24
- Domain2: 192.168.2.0/24

|设备 |域|网络|
|-----|---|-------|
|H1|Domain1|192.168.1.1/24|
|H2|Domain1|192.168.1.2/24|
|H3|Domain2|192.168.2.1/24|
|H4|Domain2|192.168.2.2/24|

2.2 SDN-IP配置
1. __BGP配置__

AS号:
- Domain1:65000
- Domain2:65002

在Quagga的配置文件中对BGP进行配置.具体在config文件夹下的quagga-sdn1.conf和quagga-sdn2.conf文件中.

BGP1的配置:

```
!
hostname bgp1
password sdnip
!
!
router bgp 65000
  bgp router-id 10.10.10.1
  timers bgp 3 9
  !
  neighbor 10.10.11.2 remote-as 65002
  neighbor 10.10.11.2 ebgp-multihop
  neighbor 10.10.11.2 timers connect 5
  neighbor 10.10.11.2 advertisement-interval 5
  !
  ! ONOS
  neighbor 10.10.10.2 remote-as 65000
  neighbor 10.10.10.2 port 2000
  neighbor 10.10.10.2 timers connect 5
  network 10.0.2.0/30
!
log stdout

```

BGP2的配置:
```
!
hostname bgp2
password sdnip
!
!
router bgp 65002
  bgp router-id 10.10.10.5
  timers bgp 3 9
  !
  neighbor 10.10.11.1 remote-as 65000
  neighbor 10.10.11.1 ebgp-multihop
  neighbor 10.10.11.1 timers connect 5
  neighbor 10.10.11.1 advertisement-interval 5
  !
  ! ONOS
  neighbor 10.10.10.6 remote-as 65002
  neighbor 10.10.10.6 port 2000
  neighbor 10.10.10.6 timers connect 5
  network 10.0.2.4/30
!
log stdout

```

2. SDN-IP应用配置

需配置:
- 域对外端口的IP用于建立eBGP对等体时的ARP代理.
- 域控制器端口的虚拟网关,用于借助SDN-IP应用进行跨域通信.

配置文件分别为network-cfg1.json, network-cfg2.json.

Domain1的SDN-IP应用配置:

Domain2的SDN-IP应用配置:


2.3 OXP配置

需对控制器进行常规的OXP配置,不再赘述.

###3. 测试
1. 启动各控制器
2. 关闭FWD应用,开启SDN-IP应用和ReactiveRouting应用
```
onos> app deactivate org.onosproject.fwd 
onos> app activate org.onosproject.sdnip
onos> app activate org.onosproject.reactive.routing
```
3. 运行网络

4. 检查BGP邻居建立与路由通告

```
onos> bgp-routes 
   Network            Next Hop        Origin LocalPref       MED BGP-ID
   10.0.2.0/30        10.10.10.1         IGP       100         0 10.10.10.1     
                      AsPath [none]
   10.0.2.4/30        10.10.11.2         IGP       100         0 10.10.10.1     
                      AsPath 65002
Total BGP IPv4 routes = 2

   Network            Next Hop        Origin LocalPref       MED BGP-ID
Total BGP IPv6 routes = 0
```
5. 测试OXP Domain与Super的连通性

在Domain主机上ping super,检查连通性.
```
mininet> root ping 10.0.2.1
*** errRun: ['stty', '-icanon', 'min', '1'] 
  0PING 10.0.2.1 (10.0.2.1) 56(84) bytes of data.
64 bytes from 10.0.2.1: icmp_seq=1 ttl=64 time=0.180 ms
64 bytes from 10.0.2.1: icmp_seq=2 ttl=64 time=0.148 ms
64 bytes from 10.0.2.1: icmp_seq=3 ttl=64 time=0.151 ms
64 bytes from 10.0.2.1: icmp_seq=4 ttl=64 time=0.181 ms
^CsendInt: writing chr(3)

--- 10.0.2.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3031ms
rtt min/avg/max/mdev = 0.148/0.165/0.181/0.015 ms

```
6. 运行OXP应用,检查OXP信道建立情况
```
onos> app activate org.onosproject.oxp         
onos> oxp-network 
{"domainCount":2,"linkCount":2,"hostCount":4,"isLoadBalance":true,"pathComputeParam":"CAP_BW","domains":[{"id":"00:00:00:00:00:00:00:02","workMode":"Advanced","capabilityType":"bandwidth","SBPTransferMode":"Normal"},{"id":"00:00:00:00:00:00:00:01","workMode":"Advanced","capabilityType":"bandwidth","SBPTransferMode":"Normal"}]}
```
6. 测试In-band方式下的数据平面通信
(1)域内测试
```
mininet> h1 ping 192.168.1.1
*** errRun: ['stty', '-icanon', 'min', '1'] 
  0PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.
64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.031 ms
64 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=0.031 ms
64 bytes from 192.168.1.1: icmp_seq=3 ttl=64 time=0.032 ms
^CsendInt: writing chr(3)

--- 192.168.1.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2042ms
rtt min/avg/max/mdev = 0.031/0.031/0.032/0.004 ms
mininet>
```
(2)域间测试
```
mininet> h1 ping 192.168.2.1
*** errRun: ['stty', '-icanon', 'min', '1'] 
  0PING 192.168.2.1 (192.168.2.1) 56(84) bytes of data.
64 bytes from 192.168.2.1: icmp_seq=1 ttl=64 time=11.2 ms
64 bytes from 192.168.2.1: icmp_seq=2 ttl=64 time=0.674 ms
64 bytes from 192.168.2.1: icmp_seq=3 ttl=64 time=0.137 ms
^CsendInt: writing chr(3)

--- 192.168.2.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2013ms
rtt min/avg/max/mdev = 0.137/4.034/11.293/5.137 ms
mininet>

```

```
mininet> h1 iperf -c 192.168.2.1 -b 10M -i2 -t5
*** errRun: ['stty', '-icanon', 'min', '1'] 
  0------------------------------------------------------------
Client connecting to 192.168.2.1, TCP port 5001
TCP window size: 85.3 KByte (default)
------------------------------------------------------------
[  3] local 192.168.1.1 port 44434 connected with 192.168.2.1 port 5001
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 2.0 sec  2.39 MBytes  10.0 Mbits/sec
[  3]  2.0- 4.0 sec  2.38 MBytes  10.0 Mbits/sec
[  3]  0.0- 5.0 sec  5.96 MBytes  10.0 Mbits/sec
mininet> 
```