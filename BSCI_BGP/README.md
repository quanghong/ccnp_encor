# Building Scalable Cisco Internetworks
![Topology](/BSCI_BGP/DBM_Inc_BGP_Diagram_lab_dmvpn.JPG)

## Init config
```bash
cp BSCI_BGP/.env_prod ./.env

backup_telnet.py
PATH_CODE: BSCI_BGP
```

## iBGP Peerings
```bash
#Check log with authentication, it might wrong or misconfigured.
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

