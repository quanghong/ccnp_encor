# Building Scalable Cisco Internetworks
![Topology](/BSCI_OSPF/DBM_Inc_OSPF_Diagram_lab_dmvpn.JPG)

## Init config
```bash
cp BSCI_OSPF/.env_prod ./.env

backup_telnet.py
PATH_CODE: BSCI_OSPF
```

## Basic OSPF
We configure Area 0 for internal network. Area 1 for DMVPNs using point-to-multipoint non-broadcast network type.
Since <b>point-to-point non-broadcast</b> network type, neighbor don't automatically establish, we have to configure neighbor on core and edge routers. And because non-broadcast, we can see Hub OSPF state is <b>"FULL/ - "</b>with Spokes
```bash
# python configure.py

R1#show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
10.255.255.7      1   FULL/DR         00:00:34    10.100.17.7     GigabitEthernet0/1
10.255.255.5      0   FULL/  -        00:01:54    172.16.123.5    Tunnel0
10.255.255.2      0   FULL/  -        00:01:59    172.16.123.2    Tunnel0
R5#show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
10.255.255.4      0   FULL/  -        00:01:59    172.16.245.4    Tunnel1
10.255.255.1      0   FULL/  -        00:01:59    172.16.123.1    Tunnel0

R1#show ip ospf int tun 0 
Tunnel0 is up, line protocol is up 
  Internet Address 172.16.123.1/24, Area 1245, Attached via Network Statement
  Process ID 100, Router ID 10.255.255.1, Network Type POINT_TO_MULTIPOINT, Cost: 1000
```

## OSPF multi-area
Confiugre and check log files to see Inter-Area (IA) routes (LSA Type 3) from area 789, 7810, 1245
```bash
                Net Link States (Area 0)

Link ID         ADV Router      Age         Seq#       Checksum
10.100.48.4     10.255.255.4    1511        0x80000005 0x000164
10.100.78.7     10.255.255.7    1509        0x80000006 0x00A19B
```

## OSPF Optimization
The least influent on interrupt connection should be prioritized to configure. So I have change order of list devices by
> list_configure_order = ['R2', 'R5', 'R1', 'R4', 'SW1', 'SW4', 'SW2', 'SW3']

As we can see, when we change network type to <b>point-to-point</b> in internal network. There will eliminate LSA Type 2 and so neighbor relationship state is <b>FULL/  -</b>. Since this is point-to-point is also <b>non-broadcast</b>, so we don't see <b>FULL/DROTHER</b>
```bash
R1#show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
10.255.255.7      0   FULL/  -        00:00:39    10.100.17.7     GigabitEthernet0/1
10.255.255.5      0   FULL/  -        700 msec    172.16.123.5    Tunnel0
10.255.255.2      0   FULL/  -        778 msec    172.16.123.2    Tunnel0

R1#show ip ospf database

            OSPF Router with ID (10.255.255.1) (Process ID 100)

# There is no LSA Type 2 (Net Link States) in Area 0 
		Router Link States (Area 0)
...
		Summary Net Link States (Area 0)

# There is no LSA Type 2 (Net Link States) in Area 1245 
		Router Link States (Area 1245)
...
		Summary Net Link States (Area 1245)
```

If we configure mismatch OSPF network type, routers will be in 2WAY state.
```bash
SW1#show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
10.255.255.8      0   FULL/  -        00:00:30    10.100.78.8     Port-channel12
10.255.255.1      1   2WAY/DROTHER    00:00:39    10.100.17.1     GigabitEtherne                        t1/1
10.255.255.9      0   FULL/  -        00:00:32    10.100.79.9     Port-channel13
10.255.255.10     0   FULL/  -        00:00:35    10.100.107.10   GigabitEtherne                        t1/0

*Oct 16 19:47:33.731: %OSPF-4-NET_TYPE_MISMATCH: Received Hello from 10.255.255.7 on GigabitEthernet0/1 indicating a  potential network type mismatch
*Oct 16 19:48:40.655: %OSPF-5-ADJCHG: Process 100, Nbr 10.255.255.7 on GigabitEthernet0/1 from FULL to DOWN, Neighbor Down: Dead timer expired   
```


## OSPF Security
Because when we set <b><i>"passive-interface default"</i></b> command, it will be delete all existed <b><i>"no passive-interface "gi/tun"</i></b> in interface configuration. So we need to prioritize which interface should be configure first or final. I note in [ospf_security.j2](/BSCI_OSPF/template/ospf_security.j2)

> Be careful, we will be lost connection while configuring when loss management connection.

If we configure wrong authentication, routers will be on <b>EXSTART/  -</b> state.
```bash
*Oct 16 20:35:07.708: %OSPF-4-NOVALIDKEY: No valid authentication send key is available on interface Tunnel0

R5#ping 10.0.0.1
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.0.0.1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 5/6/8 ms
R5#show ip ospf nei
R5#show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
10.255.255.4      0   FULL/  -        843 msec    172.16.245.4    Tunnel1
10.255.255.1      0   EXSTART/  -     787 msec    172.16.123.1    Tunnel0
```

**Check passive interfaces**
```bash
R2#show ip protocols 
Routing Protocol is "ospf 100"
  Passive Interface(s):
    GigabitEthernet0/0
    GigabitEthernet0/0.201
    GigabitEthernet0/0.202
    GigabitEthernet0/1
    GigabitEthernet0/2
    GigabitEthernet0/3
    Loopback0
    RG-AR-IF-INPUT1
```

**Check OSPF authentication interfaces**
```bash
R1#show ip ospf inter
GigabitEthernet0/1 is up, line protocol is up 
  Neighbor Count is 1, Adjacent neighbor count is 1 
    Adjacent with neighbor 10.255.255.7
  Suppress hello for 0 neighbor(s)
  Cryptographic authentication enabled
```

## OSPF Redundancy
In case, interfaces between SW1 and SW2 go down, routers will loose their neighbor and delete routes. We configure <b>virtual link</b> to keep neighbors and don't loose routes although traffic will go to another hop SW3/ SW4 to reach to vlan destination.
```bash
SW1(config)#int range gi 0/1 - 2, gi 1/2
SW1(config-if-range)#shut

SW1#ping 10.100.8.8
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.100.8.8, timeout is 2 seconds:
.....
SW1#show ip ospf neighbor 

Neighbor ID     Pri   State           Dead Time   Address         Interface
10.255.255.1      0   FULL/  -        00:00:36    10.100.17.1     GigabitEthernet1/1
10.255.255.8      0   FULL/  -        00:00:34    10.100.78.8     Port-channel12
10.255.255.9      0   FULL/  -        00:00:37    10.100.79.9     Port-channel13
10.255.255.10     0   FULL/  -        00:00:34    10.100.107.10   GigabitEthernet1/0
```

After configure a virtual link between SW1 and SW2.
```bash
SW1#show ip ospf neighbor 
Neighbor ID     Pri   State           Dead Time   Address         Interface
10.255.255.8      0   FULL/  -        00:00:33    10.100.108.8    OSPF_VL0

SW2#show ip ospf neighbor 
Neighbor ID     Pri   State           Dead Time   Address         Interface
10.255.255.7      0   FULL/  -        00:00:37    10.100.107.7    OSPF_VL0

SW1#ping 10.100.8.8       
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.100.8.8, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 3/6/9 ms
```

<b>Because interface Port-channel 12 is authenticated, so we have to configure authentication on virtual-link.</b>
<b>And because we want traffic go to SW4 before go to R1 interface vlan 7, so we configure virtual-link on area 7810.</b>

```bash
SW2#show ip route 10.100.7.0
Routing entry for 10.100.7.0/24
  Known via "ospf 100", distance 110, metric 3, type intra area
  Last update from 10.100.108.10 on Port-channel24, 00:01:43 ago
  Routing Descriptor Blocks:
  * 10.100.108.10, from 10.255.255.7, 00:01:43 ago, via Port-channel24
      Route metric is 3, traffic share count is 1

SW2#traceroute 10.100.7.7
Type escape sequence to abort.
Tracing the route to 10.100.7.7
VRF info: (vrf in name/id, vrf out name/id)
  1 10.100.108.10 3 msec 3 msec 3 msec
  2 10.100.107.7 9 msec *  5 msec
```

## OSPF Path Selection
By default, OSPF load balance traffic with equal cost path. To prefer a path than others, we configure cost on interface.
```bash
R2#show ip ospf interface tun 1
Tunnel1 is up, line protocol is up 
  Internet Address 172.16.245.2/24, Area 1245, Attached via Network Statement
  Process ID 100, Router ID 10.255.255.2, Network Type POINT_TO_MULTIPOINT, Cost: 1000

R2#show ip ospf interface tun 0
Tunnel0 is up, line protocol is up 
  Internet Address 172.16.123.2/24, Area 1245, Attached via Network Statement
  Process ID 100, Router ID 10.255.255.2, Network Type POINT_TO_MULTIPOINT, Cost: 1000

R2#traceroute 10.100.8.8
Type escape sequence to abort.
Tracing the route to 10.100.8.8
VRF info: (vrf in name/id, vrf out name/id)
  1 172.16.245.4 1 msec 4 msec 7 msec
  2 10.100.48.8 4 msec *  3 msec
```

The <b>LOWER</b> cost path will be preferred.
```bash
R2#show ip ospf interface tun 0
Tunnel0 is up, line protocol is up 
  Internet Address 172.16.123.2/24, Area 1245, Attached via Network Statement
  Process ID 100, Router ID 10.255.255.2, Network Type POINT_TO_MULTIPOINT, Cost: 100

R2#traceroute 10.100.8.8
Type escape sequence to abort.
Tracing the route to 10.100.8.8
VRF info: (vrf in name/id, vrf out name/id)
  1 172.16.123.1 10 msec 8 msec 4 msec
  2 10.100.17.7 9 msec 10 msec 8 msec
  3 10.100.78.8 9 msec *  9 msec
```

## OSPF Summarization

We have two options to summary routes and advertise it
  * If we want routers (R1, R4, R2, R5) in a same area (1245) <b>still have specific routes but only advertise summary routes to other areas</b>, we configure at ABR routers to summarize routes:
```bash
#We have specific routes in backbone area
SW1#show ip route | in 10.20
O IA     10.20.1.0/24 [110/1002] via 10.100.17.1, 00:02:43, GigabitEthernet1/1
O IA     10.20.2.0/24 [110/1002] via 10.100.17.1, 00:02:43, GigabitEthernet1/1
SW2#show ip route | in 10.20
O IA     10.20.1.0/24 [110/1002] via 10.100.48.4, 00:02:28, GigabitEthernet1/1
O IA     10.20.2.0/24 [110/1002] via 10.100.48.4, 00:02:28, GigabitEthernet1/1
```
```bash
#We summarize routes
R1# router ospf 100
R1#  area 1245 range 10.20.0.0 255.255.252.0
R4# router ospf 100
R4#  area 1245 range 10.20.0.0 255.255.252.0

#After ABR routers summarize and advertise routes
SW1#show ip route | in 10.20
O IA     10.20.0.0/22 [110/1002] via 10.100.17.1, 00:07:32, GigabitEthernet1/1
SW2#show ip route | in 10.20
O IA     10.20.0.0/22 [110/1002] via 10.100.48.4, 00:01:02, GigabitEthernet1/1
```
  * If we <b>want summarize routes as External routes and inject into area</b>. I will configure on R5 to compare with R2 by redistributing routes:
```bash
#We have specific routes in backbone area
R4(config-router)#do show ip route | in 10.50            
O E2     10.50.0.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.1.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.2.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.3.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.4.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.5.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.6.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.7.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1

#We redistribute routes
R5# router ospf 100
R5#  redistribute connected subnets
#Result
R4(config-router)#do show ip route | in 10.50            
O E2     10.50.0.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.1.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.2.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.3.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.4.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.5.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.6.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1
O E2     10.50.7.0/24 [110/20] via 172.16.245.5, 00:00:24, Tunnel1

#We summarize redustributed routes
R5# router ospf 100
R5#  summary-address 10.50.0.0 255.255.248.0
#Result
R4(config-router)#do show ip route | in 10.50
O E2     10.50.0.0/21 [110/20] via 172.16.245.5, 00:00:03, Tunnel1
R1(config-router)#do show ip route | in 10.50
O E2     10.50.0.0/21 [110/20] via 172.16.123.5, 00:00:01, Tunnel0
```

Look! We advertised IP WAN of R2, R5 into backbone area. I don't think it is good.
```bash
SW1#show ip route | in 10.20
O E2     10.0.0.0/29 [110/20] via 10.100.17.1, 00:01:49, GigabitEthernet1/1
O E2     10.0.0.8/29 [110/20] via 10.100.17.1, 00:01:49, GigabitEthernet1/1
O IA     10.20.0.0/22 [110/1002] via 10.100.17.1, 00:02:05, GigabitEthernet1/1
O E2     10.50.0.0/21 [110/20] via 10.100.17.1, 00:01:49, GigabitEthernet1/1
SW2#show ip route | in 10.20
O E2     10.0.0.0/29 [110/20] via 10.100.48.4, 00:01:54, GigabitEthernet1/1
O E2     10.0.0.8/29 [110/20] via 10.100.48.4, 00:01:54, GigabitEthernet1/1
O IA     10.20.0.0/22 [110/1002] via 10.100.48.4, 00:02:07, GigabitEthernet1/1
O E2     10.50.0.0/21 [110/20] via 10.100.48.4, 00:01:54, GigabitEthernet1/1
```

Because R5 is configured with cmd <b>redistribute connected subnets</b>. So it advertises interface WAN to OSPF process.
So we need to <b>distribute exactly prefixes from R5 except interface WAN.</b>
Finally, we can compare now. We can see route <b>IA 10.20.0.0/22 as Type 3 Summary route</b> and <b>E2 10.50.0.0/21 as Type 5 External route</b>.
```bash
SW1#show ip route | in 10.20
O IA     10.20.0.0/22 [110/1002] via 10.100.17.1, 00:17:31, GigabitEthernet1/1
O E2     10.50.0.0/21 [110/20] via 10.100.17.1, 00:02:47, GigabitEthernet1/1
SW1#show ip route | in 10.0
      10.0.0.0/8 is variably subnetted, 26 subnets, 4 masks
O        10.100.10.0/24

SW2#show ip route | in 10.20
O IA     10.20.0.0/22 [110/1002] via 10.100.48.4, 00:18:25, GigabitEthernet1/1
O E2     10.50.0.0/21 [110/20] via 10.100.48.4, 00:03:41, GigabitEthernet1/1
SW2#show ip route | in 10.0
      10.0.0.0/8 is variably subnetted, 26 subnets, 4 masks
O        10.100.10.0/24 [110/2] via 10.100.108.10, 03:38:50, Port-channel24
```

I tracert to make sure internal vlans send traffic to Tunnel interfaces by DMVPNs.
```bash
SW3#traceroute 10.50.7.5
Type escape sequence to abort.
Tracing the route to 10.50.7.5
VRF info: (vrf in name/id, vrf out name/id)
  1 10.100.89.8 3 msec
    10.100.79.7 5 msec
    10.100.89.8 2 msec
  2 10.100.17.1 5 msec
    10.100.48.4 8 msec
    10.100.17.1 6 msec
  3 172.16.245.5 9 msec
    172.16.123.5 11 msec *

SW4#traceroute 10.50.7.5
Type escape sequence to abort.
Tracing the route to 10.50.7.5
VRF info: (vrf in name/id, vrf out name/id)
  1 10.100.107.7 3 msec
    10.100.108.8 4 msec
    10.100.107.7 3 msec
  2 10.100.48.4 13 msec
    10.100.17.1 6 msec
    10.100.48.4 7 msec
  3 172.16.123.5 10 msec
    172.16.245.5 9 msec *
```

Moreover, if we look at R5 is configured with <b>distribute-list</b>, we will understand that R5 will filter the WAN routes <b>(CONNECTED_TO_OSPF deny 20 / [10.0.0.0/29, 10.0.0.8/29])</b>.
```bash
#R5
ip access-list standard CONNECTED_INTERNAL
 permit 10.50.0.0 0.0.248.255
!
route-map CONNECTED_TO_OSPF permit 10
 match ip address CONNECTED_INTERNAL
!
route-map CONNECTED_TO_OSPF deny 20
!
router ospf 100
 redistribute connected subnets route-map CONNECTED_TO_OSPF
```
_And because R5 WAN interfaces are not advertised with OSPF. So we can not configure WAN interfaces by cmd <b>summary-address ... not-advertise</b>._

