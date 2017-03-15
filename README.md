# Mininet创建网络脚本

标签（空格分隔）： Mininet

---

##说明
用于创建各种网路的Mininet脚本。起源于对In-Band网络和虚实结合的混合网络的探索，因此大多与In-Band形式的网络有关，修改相关In-Band设置后即为简单网络。

##重要文件/目录列表
1. topo_simple.py:

创建最简单的In-Band网络。

2. sdn-ip-demo1

使用Mininet搭建的SDN-IP仿真网络，又5个AS构成，其中一个AS为SDN网络。

3. sdn-ip-demo2

使用Mininet搭建的SDN-IP仿真网络，包含两个运行着SDN网络的AS，用于测试两个SDN网络通过BGP互通。

4. sdn-ip-oxp-inband目录

用于OXP组网测试的拓扑，域间普通主机的通信由OXP协议管理，OXP协议中域间Domain控制器和Super控制器连接的建立由SDN-IP负责,并且，控制器与交换机之间以In-Band方式连接。总之：
 SDN-IP + OXP + OF(In-Band)。




