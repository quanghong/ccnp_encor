# Building Scalable Cisco Internetworks

![Topology](/BSCI_EIGRP/DBM_Inc_EIGRP_Diagram_lab_dmvpn.JPG)
*I have changed border routers (R1, R4) run Frame Relay to connect to Remote sites (R2, R5), by configuring DMVPN. Because vIOS image has not serial interfaces, and I can learn DMVPN.*
![Topology](/BSCI_EIGRP/DBM_Inc_EIGRP_Diagram_lab.JPG)

## Init config
I decide to split code folders into each solution. We still have backup_configure.py to backup cfg all devices using telnet with port eve-ng.
But to resolve each solution, we need to change directory to each folder.
```bash
backup_telnet.py
PATH_CODE: BSCI_EIGRP
```

**Adding route for Ubuntu server**:
```
ping -I ens37 10.10.13.1

sudo route add -net 10.0.0.0/8 gw 192.168.20.137
ssh -B ens37 cisco@10.255.255.9
```

## DMVPN
**Config**
I configure 2 DMVPNs on each remote sites.
* DMVPN1: R1(Hub) - R2(Spoke 1), R5(Spoke 2).
  * IP network public 10.0.0.0/29
  * IP network tunnel 172.16.123.0/24
* DMVPN2: R4(Hub) - R2(Spoke 1), R5(Spoke 2).
  * IP network public 10.0.0.8/29
  * IP network tunnel 172.16.245.0/24
```bash
R1#show run int tun 0
Building configuration...

Current configuration : 196 bytes
!
interface Tunnel0
 ip address 172.16.123.1 255.255.255.0
 no ip redirects
 ip nhrp authentication DMVPN1
 ip nhrp network-id 1
 tunnel source GigabitEthernet0/0
 tunnel mode gre multipoint
end

R4#show run int tun 1
Building configuration...

Current configuration : 196 bytes
!
interface Tunnel1
 ip address 172.16.245.4 255.255.255.0
 no ip redirects
 ip nhrp authentication DMVPN2
 ip nhrp network-id 2
 tunnel source GigabitEthernet0/0
 tunnel mode gre multipoint
end

R5#show run int tun 1
Building configuration...

Current configuration : 273 bytes
!
interface Tunnel1
 ip address 172.16.245.5 255.255.255.0
 ip nhrp authentication DMVPN2
 ip nhrp map multicast 10.0.0.9
 ip nhrp map 172.16.245.4 10.0.0.9
 ip nhrp network-id 2
 ip nhrp nhs 172.16.245.4
 tunnel source GigabitEthernet0/2
 tunnel destination 10.0.0.9
end

R5#show run int tun 0
Building configuration...

Current configuration : 273 bytes
!
interface Tunnel0
 ip address 172.16.123.5 255.255.255.0
 ip nhrp authentication DMVPN1
 ip nhrp map multicast 10.0.0.1
 ip nhrp map 172.16.123.1 10.0.0.1
 ip nhrp network-id 1
 ip nhrp nhs 172.16.123.1
 tunnel source GigabitEthernet0/1
 tunnel destination 10.0.0.1
end
```
Logs
```bash
*Oct 13 03:19:49.736: NHRP: Registration with Tunnels Decap Module succeeded
*Oct 13 03:19:50.327: %LINEPROTO-5-UPDOWN: Line protocol on Interface Tunnel1, changed state to up
```

**Validate two DMVPNs, tunnel 0 and 1**
We can show dmvpn status to see R5 has two tunnels for each DMVPN.
```bash
R5#show dmvpn
Legend: Attrb --> S - Static, D - Dynamic, I - Incomplete
        N - NATed, L - Local, X - No Socket
        T1 - Route Installed, T2 - Nexthop-override
        C - CTS Capable, I2 - Temporary
        # Ent --> Number of NHRP entries with same NBMA peer
        NHS Status: E --> Expecting Replies, R --> Responding, W --> Waiting
        UpDn Time --> Up or Down Time for a Tunnel
==========================================================================

Interface: Tunnel0, IPv4 NHRP Details
Type:Spoke, NHRP Peers:1,

 # Ent  Peer NBMA Addr Peer Tunnel Add State  UpDn Tm Attrb
 ----- --------------- --------------- ----- -------- -----
     1 10.0.0.1           172.16.123.1    UP 00:29:54     S

Interface: Tunnel1, IPv4 NHRP Details
Type:Spoke, NHRP Peers:1,

 # Ent  Peer NBMA Addr Peer Tunnel Add State  UpDn Tm Attrb
 ----- --------------- --------------- ----- -------- -----
     1 10.0.0.9           172.16.245.4    UP 00:00:44     S
```
In each DMVPN, if each remote site want to send traffic to other, it has to send traffic to Hub router.
```bash
R5#traceroute 172.16.123.2
Type escape sequence to abort.
Tracing the route to 172.16.123.2
VRF info: (vrf in name/id, vrf out name/id)
  1 172.16.123.1 9 msec 9 msec 6 msec
  2 172.16.123.2 13 msec 6 msec *
```

## Enable SSH
**Enable password encryption**
```service password-encryption```

**Setting enable password**
```enable password "key-string"```

**Enable SSH with secret**
```bash
ip ssh version 2
username cisco privilege 15 secret "key-string"
!
line console 0
 login local
!
line vty 0 4
 login local
 transport input all
!
```

## Configure EIGRP and EIGRP Security
Configure all interface loopback in EIGRP for management.
**Enable EIGRP Security with correct flow**
For not interrupting the connection from Ubuntu Server to all devices. We have to configure each device with flow management.
> R5 --- R2 --- R1 --- R4 --- SW1 --- SW4 --- SW2 --- SW3

## EIGRP Convergence Optimization
EIGRP calculate metrics of routes to advertise by intended <b>primary path</b>, which is based on five K values. We can see R2, R5 learnt best route with two nexthop, to R1 or R4.
By default, EIGRP uses K1 and K3. We adjust Delay value (K3).
```bash
#R2
int gi 0/1
  delay 4000
```
Also, we can configure Hello timer and Hold timer to <b>converge faster</b> in case link down.
```bash
R1(config)#int gi 0/0
R1(config-if)#shut

R2# ping 10.100.10.10 repeat 10000
!!..!!!
```

## EIGRP Load-Balancing
As we can see in SW3, SW4 see routes from remote sites with 2 path, to R1 and R4 as a same FD. We want to load traffic more on port-channel because we have more bandwidth on it.
```bash
#SW3, SW4 show ip route eigrp
D        10.255.255.2/32 
           [90/131328] via 10.100.89.8, 00:05:45, GigabitEthernet0/2
           [90/131328] via 10.100.79.7, 00:05:45, Port-channel13
D        10.255.255.5/32 
           [90/131328] via 10.100.89.8, 00:05:45, GigabitEthernet0/2
           [90/131328] via 10.100.79.7, 00:05:45, Port-channel13

#SW3, SW4 show ip eigrp topology. 10.255.255.2/32 learnt from SW1, SW2 with same FD. FD = AD + cost./ 131328 = 131072 + 256.
# !!! So, we configure variance on SW3 and SW4 to load more traffic on preferred interface !!!
P 10.255.255.2/32, 2 successors, FD is 131328
        via 10.100.79.7 (131328/131072), Port-channel13
        via 10.100.89.8 (131328/131072), GigabitEthernet0/2

#SW1 calculate FD to 10.255.255.2/32 = 131072, with FD = AD + cost./ 131072 = 130816 + 256.
#SW1 advertise 10.255.255.2/32 to SW1 with Advertised Distance (AD) = 130816
P 10.255.255.2/32, 1 successors, FD is 131072
        via 10.100.17.1 (131072/130816), GigabitEthernet1/1
        
#R1 calculate FD to 10.255.255.2/32 = 130816, with FD = AD + cost./ 131072 = 128256 + 2560.
#R1 advertise 10.255.255.2/32 to SW1 with Advertised Distance (AD) = 130816
P 10.255.255.2/32, 1 successors, FD is 130816
        via 10.0.0.2 (130816/128256), GigabitEthernet0/0

#R2 advertise 10.255.255.2/32 to R1 with Advertised Distance (AD) = 128256. Which is equal Feasible Distance (FD) because the route learnt from conected interface.
P 10.255.255.2/32, 1 successors, FD is 128256
        via Connected, Loopback
```

## EIGRP Default route
To discard unknown traffic from network, we can create null route to advertise into network. Advertise default route as null route.
## EIGRP Stub network.
When we only want to advertise connected network.