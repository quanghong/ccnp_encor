# Building Campus Multilayer Switch Network

![Topology](/BCMSN/DBM_Inc_Campus_Diagram_lab.JPG)

**Init config**:
```
backup_telnet.py
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