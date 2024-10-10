# Building Campus Multilayer Switch Network

![Topology](/BCMSN_Gateway_Redundancy/DBM_Inc_Gateway_Redundancy_Diagram_lab.JPG)

**Init config**:
```bash
backup_telnet.py
path_code: BCMSN_Gateway_Redundancy
```

**HSRP**:
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

Configure R1 tracking interface Gi0/1. R1 will decrease its priority. So that, R4 can preempt to be Active.
```bash
R1(config)# track 1 interface GigabitEthernet0/1 line-protocol

R1(config-if)# interface GigabitEthernet0/0
R1(config-if)# standby 1 track 1 decrement 100
```