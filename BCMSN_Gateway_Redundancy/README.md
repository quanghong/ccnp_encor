# Building Campus Multilayer Switch Network

![Topology](/BCMSN_Gateway_Redundancy/DBM_Inc_Gateway_Redundancy_Diagram_lab.JPG)

**Init config**:
```
backup_telnet.py
path_code: BCMSN_Gateway_Redundancy
```

**Verify vlan, trunk, etherchannel, routes**:
```
verify.py
```

**Adding route for local interface**:
```
ping -I ens37 10.10.13.1
sudo route add -net 10.0.0.0/8 gw 192.168.20.137
```