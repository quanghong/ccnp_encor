# Network Lessons CCIE Routing & Switching

## BGP
### Path Attributes
**Weight**
* Weight attribute <b>influence on a router</b>.
* Weight <b>HIGHEST</b> is chosen.
* Setting on <b>decision router's inbound interface</b>.

```bash
R1#show ip bgp
BGP table version is 2, local router ID is 192.168.13.1
Status codes: s suppressed, d damped, h history, * valid, > best, i - internal,
              r RIB-failure, S Stale, m multipath, b backup-path, f RT-Filter,
              x best-external, a additional-path, c RIB-compressed,
              t secondary path,
Origin codes: i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

     Network          Next Hop            Metric LocPrf Weight Path
 *    2.2.2.0/24       192.168.13.3             0           200 2 i
 *>                    192.168.12.2             0           300 2 i
R1#
*Oct 20 16:14:00.631: %BGP-5-ADJCHANGE: neighbor 192.168.12.2 Up
*Oct 20 16:14:00.753: %BGP-5-ADJCHANGE: neighbor 192.168.13.3 Up
```

**Local Preference**
