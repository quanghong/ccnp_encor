# Building Campus Multilayer Switch Network

![Topology](/BCMSN_Campus/DBM_Inc_Campus_Diagram_lab.JPG)

**Init config**:
```bash
backup_telnet.py
path_code: BCMSN_Campus
```

**Verify vlan, trunk, etherchannel, routes**:
```bash
verify.py
```

**Adding route for local interface**:
```bash
ping -I ens37 10.10.13.1 # ping from specific interface

sudo route add -net 10.0.0.0/8 gw 192.168.20.137 # add route
ssh -B ens37 cisco@10.255.255.9 # bind interface
ssh -b 192.168.20.129 cisco@10.255.255.10 # bind interface address
```

**Fast way to configure port access**:
```bash
SW4(config-if)#switchport host
switchport mode will be set to access
spanning-tree portfast will be enabled
channel group will be disabled
```