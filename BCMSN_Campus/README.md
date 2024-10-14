# Building Campus Multilayer Switch Network

![Topology](/BCMSN_Campus/DBM_Inc_Campus_Diagram_lab.JPG)

**Init config**:
```
backup_telnet.py
path_code: BCMSN_Campus
```

**Verify vlan, trunk, etherchannel, routes**:
```
verify.py
```

**Adding route for local interface**:
```
ping -I ens37 10.10.13.1

sudo route add -net 10.0.0.0/8 gw 192.168.20.137
ssh -B ens37 cisco@10.255.255.9
```