# Building Scalable Cisco Internetworks
![Topology](/BSCI_BGP/DBM_Inc_BGP_Diagram_lab_dmvpn.JPG)

## Init config
```bash
cp BSCI_BGP/.env_prod ./.env

backup_telnet.py
PATH_CODE: BSCI_BGP
```

## iBGP Peerings
**iBGP split-horizon**
<b>iBGP require full-mesh connectivity between routers in a transit AS.</b>
> Transit AS:  R1 - SW1 - SW2

If only SW1 peer with R1 and SW1 peer with SW2, R1 and SW2 don't establish peering. SW1:
* SW1 <b>don't forward Open/ Update message</b> from R1 to SW2, R1 and SW2 can't establish peering.
* SW1 <b>don't advertise routes</b> to SW2 although R1, SW1, SW2 are in the same AS.

```bash
#Check log with authentication, it might wrong or misconfigured
*Oct 19 15:12:54.764: %TCP-6-BADAUTH: Invalid MD5 digest from 172.16.13.3(15096) to 172.16.13.1(179) tableid - 0Connection to 10.255.255.1 closed by remote host.

R1#show ip bgp summary
BGP router identifier 10.255.255.1, local AS number 100
BGP table version is 1, main routing table version 1

Neighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.255.255.4    4          100       4       4        1    0    0 00:01:52        0
10.255.255.7    4          100      19      18        1    0    0 00:13:31        0
10.255.255.8    4          100       4       3        1    0    0 00:01:42        0
172.16.13.3     4          300       0       0        1    0    0 never    Active
```

## eBGP Peerings
We configure eBGP peerings on core routers. ISP routers advertise its internal network to core routers.
```bash
R4#show ip bgp summary 
Neighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.255.255.1    4          100      60      72       37    0    0 00:46:11       12
10.255.255.7    4          100      59      66       37    0    0 00:46:09        0
10.255.255.8    4          100      60      61       37    0    0 00:45:55        0
172.16.46.6     4          600    1509    1318       37    0    0 00:22:22       12

R1#show ip bgp summary 
Neighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.255.255.4    4          100      72      60       49    0    0 00:45:56       12
10.255.255.7    4          100      73      72       49    0    0 00:57:35        0
10.255.255.8    4          100      34      40       49    0    0 00:25:49        0
172.16.13.3     4          300      46      51       49    0    0 00:36:06       12
```

## iBGP next-hop-self
<b>By default, router don't change Next Hop when advertising routes to its neighbor</b>. So, we configure R4 next-hop-self to the routes it advertise to R1.

```bash
R4#show ip bgp neighbors 10.255.255.1 advertised-routes 
     Network          Next Hop            Metric LocPrf Weight Path
 *>   2.0.0.0/24       172.16.46.6              0             0 600 600 600 600 8543 i
Total number of prefixes 12 

R1#show ip bgp
     Network          Next Hop            Metric LocPrf Weight Path
 *>i  2.0.0.0/24       172.16.46.6              0    100      0 600 600 600 600 8543 i

#Result
R1#show ip bgp
     Network          Next Hop            Metric LocPrf Weight Path
 *>i  2.0.0.0/24       10.255.255.4             0    100      0 600 600 600 600 8543 i
```

## BGP NLRI Advertisements
<b>Now core routers only ping to its ISP network</b>, because we have not configure NLRI Advertisements.

```bash
R4#ping 2.0.0.1
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 2.0.0.1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 2/2/4 ms

R1#ping 2.0.0.1
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 2.0.0.1, timeout is 2 seconds:
.....
Success rate is 0 percent (0/5)

R1#ping 172.16.46.6
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 172.16.46.6, timeout is 2 seconds:
.....
Success rate is 0 percent (0/5)
```

<b>If we want to advertise network in BGP we need to type the exact subnet mask for the network we want to advertise.</b>
If I type <b>network 10.100.7.0 mask 255.255.240.0</b> on R1 it will not work since this entry is not in the routing table.

```bash
R1(config-router)#network 10.100.7.0 mask 255.255.240.0 
% BGP: Incorrect network or mask/prefix-length configured
```

## BGP Routes Aggregation
With network [10.100.7.0/24, 10.100.8.0/24, 10.100.9.0/24, 10.100.10.0/24], we can summarize with <b>10.100.0.0/20</b>.
But we only want to summarize with minimum networks and only advertise routes in DBMI network, so we only summarize ranges [10.100.8.0/24, 10.100.9.0/24, 10.100.10.0/24] with <b>10.100.8.0 and a single network \[10.100.7.0/24]</b>.

```bash
#R1 summarize wide range network.
 *>   10.20.0.0/22     0.0.0.0                            32768 i
 *>   10.50.0.0/21     0.0.0.0                            32768 i
 *>   10.100.0.0/20    0.0.0.0                            32768 i
#R1 summarize smallest
R1#show ip bgp neighbors 172.16.13.3 advertised-routes
 *>   10.20.0.0/22     0.0.0.0                            32768 i
 *>   10.50.0.0/21     0.0.0.0                            32768 i
 *>   10.100.7.0/24    10.100.17.7              2         32768 i
 *>   10.100.8.0/22    0.0.0.0                            32768 i

R4#show ip bgp neighbors 172.16.46.6 advertised-routes
 *>   10.20.0.0/22     0.0.0.0                            32768 i
 *>   10.50.0.0/21     0.0.0.0                            32768 i
 *>   10.100.0.0/20    0.0.0.0                            32768 i
```

## Outbound BGP Path Selection
We want to prefer all traffic will send to ISP2. So we choose <b>Local Preference</b> path attribute because Local Preference will <b>influence to all routers in an AS and R4 is a decision router, then we set policy on R4's inbound interface</b>.
Local Preference <b>HIGHER</b> will be chosen.
```bash
R1#show ip bgp 1.0.0.0
BGP routing table entry for 1.0.0.0/10, version 10
Paths: (1 available, best #1, table default)
  Advertised to update-groups:
     5         
  Refresh Epoch 1
  300
    172.16.13.3 from 172.16.13.3 (192.168.3.1)
      Origin incomplete, metric 0, localpref 100, valid, external, best
      rx pathid: 0, tx pathid: 0x

#Result after setting Local Preference.
R1# show ip bgp 1.0.0.0
BGP routing table entry for 1.0.0.0/10, version 248
Paths: (2 available, best #1, table default)
  Advertised to update-groups:
     6         
  Refresh Epoch 2
  600 300
    10.255.255.4 (metric 4) from 10.255.255.4 (10.255.255.4)
      Origin incomplete, metric 0, localpref 1000, valid, internal, best
      rx pathid: 0, tx pathid: 0x0
  Refresh Epoch 1
  300
    172.16.13.3 from 172.16.13.3 (192.168.3.1)
      Origin incomplete, metric 0, localpref 100, valid, external
      rx pathid: 0, tx pathid: 0
```

## Inbound BGP Path Selection
We have <b>Multi-Exit Discriminator and AS PATH prepending path attributes to influence Next Hop device to choose which path to go to local AS</b>.
We configure AS PATH prepending on R1 to influence R3 forward traffic to R6, then send traffic to R4 to reach to DMBI networks.
```bash
R3#show ip bgp
     Network          Next Hop            Metric LocPrf Weight Path
 *>   2.0.0.0/24       172.16.13.1                            0 100 600 ?
 *>   2.0.18.0/24      172.16.13.1                            0 100 600 ?
 *>   2.0.35.0/24      172.16.13.1                            0 100 600 ?

#Result after setting AS PATH prepending.
R3#show ip bgp
     Network          Next Hop            Metric LocPrf Weight Path
 *    2.0.0.0/24       172.16.13.1                            0 100 100 100 100 100 100 600 600 600 600 8543 i
 *>                    172.16.36.6              0             0 600 600 600 600 8543 i
 *    2.0.18.0/24      172.16.13.1                            0 100 100 100 100 100 100 600 600 600 600 8543 i
 *>                    172.16.36.6              0             0 600 600 600 600 8543 i
 *    2.0.35.0/24      172.16.13.1                            0 100 100 100 100 100 100 600 600 600 600 8543 i
```