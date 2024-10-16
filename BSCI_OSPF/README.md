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
```

## OSPF multi-area
Confiugre and check log files to see Inter-Area (IA) routes (LSA Type 3)