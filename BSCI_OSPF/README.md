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
