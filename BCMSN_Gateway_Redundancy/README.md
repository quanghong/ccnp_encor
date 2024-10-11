# Building Campus Multilayer Switch Network

![Topology](/BCMSN_Gateway_Redundancy/DBM_Inc_Gateway_Redundancy_Diagram_lab.JPG)

## Init config
```bash
backup_telnet.py
path_code: BCMSN_Gateway_Redundancy
```

## HSRP
**Checking standby status**
R1 interface Gi0/0 is down. R4 preempt to be Active.
```bash
R1# show standby brief
                     P indicates configured to preempt.
                     |
Interface   Grp  Pri P State   Active          Standby         Virtual IP
Gi0/0       1    150 P Active  local           10.100.14.4     10.100.14.254

R4#show standby brief
                     P indicates configured to preempt.
                     |
Interface   Grp  Pri P State   Active          Standby         Virtual IP
Gi0/0       1    100 P Standby 10.100.14.1     local           10.100.14.254
```

**Configuring interface tracking**
Configure R1 tracking interface Gi0/1. R1 will decrease its priority. So that, R4 can preempt to be Active.
```bash
R1(config)# track 1 interface GigabitEthernet0/1 line-protocol

R1(config-if)# interface GigabitEthernet0/0
R1(config-if)# standby 1 track 1 decrement 100
```

**Configuring IP SLA**
Tracking remote device's interface.
```bash
R1(config)#int gi 0/0
R1(config-if)#no standby 1 track 1
R1(config)#no track 1

R1(config)#ip sla 1
R1(config-ip-sla)#icmp-echo 172.16.13.3
R1(config)#ip sla schedule 1 start-time now life forever

R1(config)#int gi 0/0
R1(config-if)#standby 1 track 1 decrement 60
```
Logs.
```bash
#R1
*Oct 10 17:59:27.609: %TRACK-6-STATE: 1 ip sla 1 state Up -> Down
*Oct 10 17:59:27.901: %HSRP-5-STATECHANGE: GigabitEthernet0/0 Grp 1 state Active -> Speak
*Oct 10 17:59:28.916: %HSRP-5-STATECHANGE: GigabitEthernet0/0 Grp 1 state Speak -> Standby

#R4
*Oct 10 18:01:15.852: %HSRP-5-STATECHANGE: GigabitEthernet0/0 Grp 1 state Standby -> Active
```

## VRRP
**Checking vrrp status**
```bash
R1#show vrrp brief
Interface          Grp Pri Time  Own Pre State   Master addr     Group addr
Gi0/0              1   150 1006       Y  Master  10.100.14.1     10.100.14.254

R4#show vrrp brief
Interface          Grp Pri Time  Own Pre State   Master addr     Group addr
Gi0/0              1   100 1608       Y  Backup  10.100.14.1     10.100.14.254

R4#show vrrp
GigabitEthernet0/0 - Group 1
  State is Backup
  Virtual IP address is 10.100.14.254
  Virtual MAC address is 0000.5e00.0101
  Advertisement interval is 0.333 sec
  Preemption enabled
  Priority is 100
  Authentication MD5, key-string
  Master Router is 10.100.14.1, priority is 150
  Master Advertisement interval is 1.000 sec
  Master Down interval is 1.608 sec (expires in 1.343 sec)
```
Logs.
```bash
#R1
*Oct 10 18:48:18.399: %TRACK-6-STATE: 1 ip sla 1 state Up -> Down
*Oct 10 18:49:57.235: %VRRP-6-STATECHANGE: Gi0/0 Grp 1 state Master -> Backup

#R4
*Oct 10 18:55:11.865: %VRRP-6-STATECHANGE: Gi0/0 Grp 1 state Backup -> Master
```

**Tracert**
After interface ISP 1 goes down. Traffic from R6 go through Backup Router (R4).
```bash
R6#traceroute 5.5.5.5
Type escape sequence to abort.
Tracing the route to 5.5.5.5
VRF info: (vrf in name/id, vrf out name/id)
  1 10.100.14.4 1010 msec 9 msec 9 msec
  2 172.16.45.5 12 msec 9 msec *
```

### VRRP Load-Balancing per group
VRRP can load-balancing traffic per group/ per VLAN, not per-packet.
```bash
#R1
interface GigabitEthernet0/0
 vrrp 2 ip 10.100.25.254

#R2
interface GigabitEthernet0/0
 vrrp 2 ip 10.100.25.254
 vrrp 2 priority 150
```

## GLBP
**Checking glbp status**
R1 is Active Virtual Gateway (priority 150). R4 is Active Virtual Forwader (priority 100).
We have 2 two virtual MAC address:
* R1: 0007.b400.0101
* R2: 0007.b400.0102
```bash
R1#show glbp brief
Interface   Grp  Fwd Pri State    Address         Active router   Standby router
Gi0/0       1    -   150 Active   10.100.14.254   local           10.100.14.4
Gi0/0       1    1   -   Active   0007.b400.0101  local           -
Gi0/0       1    2   -   Listen   0007.b400.0102  10.100.14.4     -

R4#show glbp brief
Interface   Grp  Fwd Pri State    Address         Active router   Standby router
Gi0/0       1    -   100 Standby  10.100.14.254   10.100.14.1     local
Gi0/0       1    1   -   Listen   0007.b400.0101  10.100.14.1     -
Gi0/0       1    2   -   Active   0007.b400.0102  local           -
```

We can see R2, R6 have same default gateway but different MAC address. This is how GLBP load balance traffic.
```bash
R2#show arp
Protocol  Address          Age (min)  Hardware Addr   Type   Interface
...
Internet  10.100.14.254           0   0007.b400.0102  ARPA   GigabitEthernet0/2

R6#show arp
Protocol  Address          Age (min)  Hardware Addr   Type   Interface
...
Internet  10.100.14.254           0   0007.b400.0101  ARPA   GigabitEthernet0/2
```

GLBP default weighting is 100. We set if interface uplink R1 down, R1 will decrease its weighting.
If weighting is lower 70. It become AVF, R4 will be AVG.
```bash
#R1
R1#glbp 1 weighting 100 lower 70 upper 90

R1#show glbp | in Weigh
Weighting 60, low (configured 100), thresholds: lower 70, upper 90
```
Logs.
```bash
#R1
*Oct 10 20:37:25.330: %GLBP-6-FWDSTATECHANGE: GigabitEthernet0/0 Grp 1 Fwd 1 state Active -> Listen
#R4
*Oct 10 20:53:56.672: %GLBP-6-FWDSTATECHANGE: GigabitEthernet0/0 Grp 1 Fwd 1 state Listen -> Active
```
