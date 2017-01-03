# sdn-ip-oxp-in-band

标签（空格分隔）： oxp sdn-ip in-band

---

##项目描述
  用于OXP组网测试的拓扑，域间普通主机的通信由OXP协议管理，OXP协议中域间Domain控制器和Super控制器连接的建立由SDN-IP负责,并且，控制器与交换机之间以In-Band方式连接。总之：
  SDN-IP + OXP + OF(In-Band)。

###1. 网络拓扑

![网络拓扑图](https://raw.githubusercontent.com/paradisecr/mininet-script/master/sdn-ip-oxp-inband/assets/topo-phy.png)

###2. 网络配置
2.1 网络配置

1. OF控制平面网络(In-Band下也是数据平面的一部分)

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

2. SDN-IP网络

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

4. 数据平面网络

2.2 SDN-IP配置

2.3 OXP配置

###3. 测试


