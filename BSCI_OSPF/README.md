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

Addition, we can see <b>ABR routers (R1, R4) advertise LSA Type 4 to notify that if traffic on Area 0 want to reach to external routes, then send to it.</b>
```bash
R1# show ip ospf database
                Summary ASB Link States (Area 0)
Link ID         ADV Router      Age         Seq#       Checksum
10.255.255.5    10.255.255.1    168         0x80000001 0x009A9B
10.255.255.5    10.255.255.4    170         0x80000001 0x0088AA

R4#show ip ospf database asbr-summary 
            OSPF Router with ID (10.255.255.4) (Process ID 100)
                Summary ASB Link States (Area 0)

  LS age: 26
  Options: (No TOS-capability, DC, Upward)
  LS Type: Summary Links(AS Boundary Router)
  Link State ID: 10.255.255.5 (AS Boundary Router address)
  Advertising Router: 10.255.255.1
  LS Seq Number: 80000001
  Checksum: 0x9A9B
  Length: 28
  Network Mask: /0
        MTID: 0         Metric: 1000 

  LS age: 22
  Options: (No TOS-capability, DC, Upward)
  LS Type: Summary Links(AS Boundary Router)
  Link State ID: 10.255.255.5 (AS Boundary Router address)
  Advertising Router: 10.255.255.4
  LS Seq Number: 80000001
  Checksum: 0x88AA
  Length: 28
  Network Mask: /0
        MTID: 0         Metric: 1000
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

## OSPF Stub Areas
### Not So Stubby Area and Totally NSSA
We can <b>optimize LSDB with stub areas</b>. As we can see R2 have multiple LSA Type 3 Summary routes from HQ1, HQ2, Branch and Warehouse, but actually R2 only need to reach to R1 to reach to internal routes (default route). R5 is same as R2.
So we configure <b>Totally NSSA</b> networks, because R5 has connected networks that are not in OSPF, and it becomes ASBR.
We configure R1, R4 are <b>ABR routers because they can advertise default routes into Totally NSSA</b>.
```bash
R2#show ip ospf database      
            OSPF Router with ID (10.255.255.2) (Process ID 100)
                Router Link States (Area 1245)
...
                Summary Net Link States (Area 1245)
Link ID         ADV Router      Age         Seq#       Checksum
10.100.7.0      10.255.255.1    1034        0x80000007 0x00AC08
10.100.7.0      10.255.255.4    156         0x8000000A 0x009E0F
...
192.168.20.0    10.255.255.4    1878        0x8000000A 0x009411
...
                Type-5 AS External Link States
          
Link ID         ADV Router      Age         Seq#       Checksum Tag
10.50.0.0       10.255.255.5    1991        0x80000002 0x006DED 0
```

By default in NSSA, we have to configure default route in ABRs by cmd _<b>area X nssa default-information-originate</b>_.
But in Totally NSSA, ABR routers automatically advertise default route in area.
```bash
#ABR routers
R1#show ip route | in 10.20
O        10.20.0.0/22 is a summary, 00:04:13, Null0
O        10.20.1.0/24 [110/1001] via 172.16.123.2, 00:04:13, Tunnel0
O        10.20.2.0/24 [110/1001] via 172.16.123.2, 00:04:13, Tunnel0
O N2     10.50.0.0/21 [110/20] via 172.16.123.5, 00:04:03, Tunnel0
R4# show ip route | in 10.20
O        10.20.0.0/22 is a summary, 00:04:00, Null0
O        10.20.1.0/24 [110/1001] via 172.16.245.2, 00:04:00, Tunnel1
O        10.20.2.0/24 [110/1001] via 172.16.245.2, 00:04:00, Tunnel1
O N2     10.50.0.0/21 [110/20] via 172.16.245.5, 00:04:00, Tunnel1
```

We can see R5, R2 don't exchange LSA Type 2 anymore, because they will get to ABR routers to reach to each other.
```bash
#ASBR router (R5) and other router (R2)
R2#show ip ospf database 
                Summary Net Link States (Area 1245)
Link ID         ADV Router      Age         Seq#       Checksum
0.0.0.0         10.255.255.1    532         0x80000001 0x00D852
0.0.0.0         10.255.255.4    509         0x80000001 0x00C661

                Type-7 AS External Link States (Area 1245)
Link ID         ADV Router      Age         Seq#       Checksum Tag
10.50.0.0       10.255.255.5    520         0x80000001 0x008FB3 0

R5#show ip ospf database 
                Summary Net Link States (Area 1245)
Link ID         ADV Router      Age         Seq#       Checksum
0.0.0.0         10.255.255.1    543         0x80000001 0x00D852
0.0.0.0         10.255.255.4    525         0x80000001 0x00C661

                Type-7 AS External Link States (Area 1245)
Link ID         ADV Router      Age         Seq#       Checksum Tag
10.50.0.0       10.255.255.5    530         0x80000001 0x008FB3 0


R2#show ip route ospf
O*IA  0.0.0.0/0 [110/101] via 172.16.123.1, 00:07:52, Tunnel0
O N2     10.50.0.0/21 [110/20] via 172.16.123.1, 00:04:47, Tunnel0

R5#show ip route ospf
O*IA  0.0.0.0/0 [110/101] via 172.16.245.4, 00:04:46, Tunnel1
O        10.20.1.0/24 [110/1101] via 172.16.245.4, 00:04:46, Tunnel1
O        10.20.2.0/24 [110/1101] via 172.16.245.4, 00:04:46, Tunnel1
```

And we can see R1 change LSA Type 7 route to LSA Type 5 route and advertise it to backbone area.
```bash
SW3#show ip route | in 10.20
O IA     10.20.0.0/22 [110/1003] via 10.100.89.8, 00:02:21, GigabitEthernet0/2
O E2     10.50.0.0/21 [110/20] via 10.100.89.8, 00:02:16, GigabitEthernet0/2
                      [110/20] via 10.100.79.7, 00:02:16, Port-channel13
SW4#show ip route | in 10.20
O IA     10.20.0.0/22 [110/1003] via 10.100.108.8, 00:00:26, Port-channel24
O E2     10.50.0.0/21 [110/20] via 10.100.108.8, 00:00:21, Port-channel24
                      [110/20] via 10.100.107.7, 00:00:21, GigabitEthernet0/1
```

### Stubby Area and Totally Stubby Area
Also with <b>optimizing LSDB in the Area 789, 7810</b>. We configure <b>SW1, SW2, SW4 in Stubby Area. SW1, SW2, SW3 in Totally Stubby Area</b>, _to compare LSA Type 5 route are advertised in Stubby Area, but not in Totally Stubby Area._

**Stubby Area**
Before we configure Stubby Area. Area 789 still exchange LSA Type 5 External route.
```bash
SW3#show ip ospf database
                Type-5 AS External Link States

Link ID         ADV Router      Age         Seq#       Checksum Tag
10.50.0.0       10.255.255.4    157         0x80000001 0x002A24 0         
```

After we configure Stubby Area. <b>ABR routers SW1, SW2 don't advertise LSA Type 5 External route (10.50.0.0/21) into Stubby area (area 789), but still advertise LSA Type 3 Summary route (10.20.0.0/22)</b>.
Instead, ABR routers advertise default route into Stubby area to reach to (10.50.0.0/21).
And because of Stubby Area, so SW3 still have other ospf _<b>IA routes</b>_. We can compare SW3 and SW4 routing table after.
```bash
SW1#show ip ospf database
                Type-5 AS External Link States
Link ID         ADV Router      Age         Seq#       Checksum Tag
10.50.0.0       10.255.255.4    239         0x80000001 0x002A24 0

SW1#show ip ospf route
O IA     10.20.0.0/22 [110/1002] via 10.100.17.1, 00:02:02, GigabitEthernet1/1
O E2     10.50.0.0/21 [110/20] via 10.100.17.1, 00:02:02, GigabitEthernet1/1

SW3#show ip route | in 10
Gateway of last resort is 10.100.89.8 to network 0.0.0.0
O*IA  0.0.0.0/0 [110/2] via 10.100.89.8, 00:01:17, GigabitEthernet0/2
                [110/2] via 10.100.79.7, 00:01:07, Port-channel13
      10.0.0.0/8 is variably subnetted, 23 subnets, 3 masks
O IA     10.20.0.0/22 [110/1003] via 10.100.89.8, 00:01:17, GigabitEthernet0/2
                      [110/1003] via 10.100.79.7, 00:01:07, Port-channel13

#We make sure SW3 still reach to R5 internal routes
SW3#ping 10.50.7.5
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.50.7.5, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 5/7/9 ms
SW3#
```

**Totally Stubby Area**
We need to remove virtual link configuration to test Totally Stubby on area 789.
```bash
SW1(config-router)#        area 7810 stub no-summary
% OSPF: Area cannot be a stub as it contains a virtual link
```

Finally, after we configure Totally Stubby Area. <b>ABR routers SW1, SW2 don't advertise LSA Type 5 External route into Totally Stubby area (area 789), and also don't advertise LSA Type 3 Summary route</b>.
Instead, ABR routers advertise default route into Stubby area to reach to (10.50.0.0/21).
```bash
#Before
SW4#show ip ospf database
                Summary ASB Link States (Area 7810)
Link ID         ADV Router      Age         Seq#       Checksum
10.255.255.1    10.255.255.7    139         0x80000001 0x0074AA
10.255.255.1    10.255.255.8    139         0x80000001 0x0078A4
10.255.255.4    10.255.255.7    139         0x80000001 0x0060BA
10.255.255.4    10.255.255.8    139         0x80000001 0x0050CA

                Type-5 AS External Link States
Link ID         ADV Router      Age         Seq#       Checksum Tag
10.50.0.0       10.255.255.4    117         0x80000001 0x002A24 0 

#After confiure Totally Stubby Area
SW4#show ip ospf database
            OSPF Router with ID (10.255.255.10) (Process ID 100)

		Router Link States (Area 7810)
Link ID         ADV Router      Age         Seq#       Checksum Link count
10.255.255.7    10.255.255.7    56          0x8000001C 0x001305 2         
10.255.255.8    10.255.255.8    52          0x80000024 0x0023E7 2         
10.255.255.10   10.255.255.10   50          0x80000026 0x005315 6         

		Summary Net Link States (Area 7810)
Link ID         ADV Router      Age         Seq#       Checksum
0.0.0.0         10.255.255.7    66          0x80000001 0x002DFF
0.0.0.0         10.255.255.8    58          0x80000001 0x002705

#Compare routing table of SW3, SW4 now, we will see SW4 only has one route. This is default route.
SW4#show ip route ospf
O*IA  0.0.0.0/0 [110/2] via 10.100.108.8, 00:07:11, Port-channel24

#Verify
SW4#ping 10.50.7.5
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.50.7.5, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 6/9/14 ms
```

**Modify advertise default route target**
As we can see in [OSPF Summarization](/BSCI_OSPF#ospf-summarization), SW3 and SW4 they load balance traffic with two paths, to SW1 and SW2 to reach to external routes.
But we only want SW3, SW4 send traffic to their Port-Channel interface which is higher bandwidth load. We can modify SW1, SW2 advertise default route.
```bash
#Before we configure cost
#SW3
O*IA  0.0.0.0/0 [110/2] via 10.100.108.8, 00:13:30, Port-channel24
                [110/2] via 10.100.107.7, 00:13:30, GigabitEthernet0/1

#So now SW3 only send traffic through its Port-Channel to reach to external route
#SW3
O*IA  0.0.0.0/0 [110/101] via 10.100.79.7, 00:00:03, Port-channel13

SW3#traceroute 10.50.7.5
Type escape sequence to abort.
Tracing the route to 10.50.7.5
VRF info: (vrf in name/id, vrf out name/id)
  1 10.100.79.7 2 msec 1 msec 2 msec
  2 10.100.17.1 10 msec 7 msec 9 msec
  3 172.16.123.5 8 msec *  11 msec

#We configure on Area 7810 to see SW4 send traffic to its Port-Channel
SW4#traceroute 10.50.7.5
Type escape sequence to abort.
Tracing the route to 10.50.7.5
VRF info: (vrf in name/id, vrf out name/id)
  1 10.100.108.8 2 msec 4 msec 4 msec
  2 10.100.48.4 16 msec 10 msec 6 msec
  3 172.16.245.5 11 msec *  8 msec
```

