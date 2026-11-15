# Border Gateway Protocol

> **Applies to:** BGP-4 concepts with Cisco IOS XE, Arista EOS, Junos, FRRouting, and BIRD verification examples
> **Last reviewed:** 2026-11-14

Border Gateway Protocol (BGP) is the path-vector protocol used between autonomous systems on the Internet and, increasingly, as the underlay and overlay control plane inside data centers. This sheet covers session establishment, path selection, policy tools, and verification. See [leaf-spine design](leaf-spine.md) for the fabric underlay pattern and [BIRD](../network-platforms/bird.md) or [Junos](../network-platforms/junos.md) for platform command detail.

## Safety

> [!WARNING]
> A BGP policy mistake can leak routes to other networks or withdraw your own prefixes. Review the exact advertised and received route sets before and after every change, and apply policy changes with a soft refresh instead of a session reset.

- A hard clear (`clear ip bgp *`, `clear bgp neighbor`) tears sessions down and withdraws every route learned over them. Use soft or route-refresh variants unless a reset is the goal.
- Never bring up an external session without an import policy, an export policy, and a maximum-prefix limit.
- Removing or changing a route map, prefix list, or community list that a neighbor references can change the advertised set immediately.
- Changing the router ID, local AS, or address-family activation resets sessions.
- Graceful shutdown (the `GRACEFUL_SHUTDOWN` community, RFC 8326) drains traffic before maintenance; prefer it over shutting a session abruptly.

## Quick reference

### Session types

| Type | Peers | Typical behavior |
|---|---|---|
| eBGP | Different AS numbers | TTL 1 by default, next hop set to self, AS prepended on export, administrative distance 20 on Cisco and Arista |
| iBGP | Same AS number | TTL 255, next hop unchanged, routes learned from one iBGP peer are not re-advertised to another, distance 200 |
| Multihop eBGP | Different AS, not directly connected | Requires `ebgp-multihop` or a TTL-security setting and a route to the peer address |

The iBGP re-advertisement rule requires a full mesh, route reflectors (RFC 4456), or confederations.

AS number ranges:

| Range | Use |
|---|---|
| 64512–65534 | Private 16-bit |
| 4200000000–4294967294 | Private 32-bit |
| 64496–64511, 65536–65551 | Documentation |
| 23456 | `AS_TRANS`, a placeholder seen when a 4-byte AS crosses a 2-byte-only speaker |

### Session states

| State | Meaning | If stuck here |
|---|---|---|
| Idle | Not attempting, or backing off after an error | Neighbor shut down, no route to peer, max-prefix tripped |
| Connect | TCP connection in progress | Reachability, ACL or firewall on TCP 179 |
| Active | Listening and retrying TCP | Wrong peer address or update source, peer not configured, TTL or multihop |
| OpenSent | OPEN sent, waiting for the peer's OPEN | AS number mismatch, authentication mismatch |
| OpenConfirm | Waiting for KEEPALIVE | Capability or hold-time negotiation |
| Established | Routes are exchanged | Zero prefixes: address family not activated or policy rejects everything |

A session flapping between `Active` and `Idle` is almost always reachability, source address, TTL, or authentication. A session that reaches `Established` and then resets on a timer points to an MTU problem on large UPDATE messages or a hold-timer expiry under CPU load.

Default timers are commonly 60 seconds keepalive and 180 seconds hold (Junos uses 30 and 90). The lower hold time offered by either side is used. For fast failure detection, use BFD instead of aggressive BGP timers.

### Best-path selection

Compared in order until one path wins. A path is considered only if its next hop is reachable.

| Step | Attribute | Preferred | Scope |
|---|---|---|---|
| 1 | Weight | Highest | Local to one router (Cisco and Arista only) |
| 2 | Local preference | Highest | Whole AS; default 100 |
| 3 | Locally originated | Local over learned | `network`, `redistribute`, `aggregate` |
| 4 | AS path length | Shortest | Prepending lengthens it |
| 5 | Origin | IGP over EGP over incomplete | |
| 6 | MED | Lowest | Compared only between paths from the same neighbor AS by default |
| 7 | eBGP over iBGP | eBGP | |
| 8 | IGP metric to next hop | Lowest | Hot-potato routing |
| 9 | Age, then router ID | Oldest eBGP path, then lowest router ID | Tie-breakers |
| 10 | Cluster list length, then neighbor address | Shortest, then lowest | Route-reflector tie-breakers |

Junos has no weight, compares local preference first, and evaluates route preference before BGP attributes. ECMP needs `maximum-paths` (Cisco, Arista, FRRouting) or `multipath` (Junos), and in a fabric with a different AS per leaf it also needs `bestpath as-path multipath-relax` or the Junos `multiple-as` option.

Influencing traffic:

| Goal | Tool | Applied |
|---|---|---|
| Choose the exit for outbound traffic | Local preference | Inbound policy |
| Influence the entry for inbound traffic | AS-path prepending, MED, more-specific prefixes, provider communities | Outbound policy |
| Drain a device before maintenance | `GRACEFUL_SHUTDOWN` community or lowered local preference | Both directions |

### Communities

| Type | Format | Notes |
|---|---|---|
| Standard (RFC 1997) | `<asn>:<value>`, 16 bits each | Most widely supported |
| Extended (RFC 4360) | Typed, such as `target:<asn>:<value>` | Route targets for VPNs and EVPN |
| Large (RFC 8092) | `<asn>:<value>:<value>`, 32 bits each | Use with 4-byte AS numbers |

Well-known values: `no-export` (do not advertise outside the AS or confederation), `no-advertise` (do not advertise to any peer), `local-AS` or `no-export-subconfed`, `blackhole` (65535:666, RFC 7999), and `graceful-shutdown` (65535:0). Cisco IOS XE does not send communities unless `send-community` is configured for the neighbor.

### Address families

A session carries only the address families both sides negotiate. On Cisco IOS XE and FRRouting, each neighbor must be activated under each address family; a session can be `Established` and carry no routes when it is not.

| Address family | Use |
|---|---|
| IPv4 and IPv6 unicast | Internet and underlay routing |
| VPNv4 and VPNv6 | MPLS L3VPN |
| L2VPN EVPN | VXLAN and MPLS overlays |
| IPv4 and IPv6 labeled unicast | Seamless MPLS, inter-AS options |
| Flowspec | Distributed filtering and DDoS mitigation |

RFC 8950 allows IPv4 routes with an IPv6 next hop, which is the basis of BGP unnumbered fabrics.

### Verification commands

| Task | Cisco IOS XE | Arista EOS | Junos |
|---|---|---|---|
| Session summary | `show bgp ipv4 unicast summary` | `show ip bgp summary` | `show bgp summary` |
| One neighbor | `show bgp ipv4 unicast neighbors <peer-ip>` | `show ip bgp neighbors <peer-ip>` | `show bgp neighbor <peer-ip>` |
| Routes received before policy | `show bgp ipv4 unicast neighbors <peer-ip> received-routes` | `show ip bgp neighbors <peer-ip> received-routes` | `show route receive-protocol bgp <peer-ip>` |
| Routes accepted | `show bgp ipv4 unicast neighbors <peer-ip> routes` | `show ip bgp neighbors <peer-ip> routes` | `show route protocol bgp source-gateway <peer-ip>` |
| Routes advertised | `show bgp ipv4 unicast neighbors <peer-ip> advertised-routes` | `show ip bgp neighbors <peer-ip> advertised-routes` | `show route advertising-protocol bgp <peer-ip>` |
| One prefix, all paths | `show bgp ipv4 unicast <prefix>` | `show ip bgp <prefix> detail` | `show route <prefix> detail` |
| Soft refresh inbound | `clear bgp ipv4 unicast <peer-ip> soft in` | `clear ip bgp <peer-ip> soft in` | `clear bgp neighbor <peer-ip> soft-inbound` |
| Soft refresh outbound | `clear bgp ipv4 unicast <peer-ip> soft out` | `clear ip bgp <peer-ip> soft out` | `clear bgp neighbor <peer-ip> soft` |

On Cisco IOS XE, `received-routes` needs `soft-reconfiguration inbound` on the neighbor. On Junos, `receive-protocol` shows routes before import policy except those rejected for a loop or an unusable next hop; add `hidden` to see rejected routes.

FRRouting and BIRD:

```bash
vtysh -c "show bgp summary"
vtysh -c "show bgp ipv4 unicast neighbors <peer-ip> advertised-routes"
vtysh -c "show bgp ipv4 unicast <prefix>"
birdc show protocols all <bgp-instance>
birdc show route export <bgp-instance>
birdc show route for <ip-address> all
```

### Baseline hardening for external sessions

- Explicit import and export policy on every eBGP session. RFC 8212 makes "no policy, no routes" the default; FRRouting and IOS XR enforce it, while classic IOS XE, Arista EOS, and Junos exchange routes without a policy unless configured otherwise.
- Maximum-prefix limit per neighbor and address family, with a warning threshold.
- Prefix filters that reject bogons, your own prefixes inbound, and anything longer than /24 (IPv4) or /48 (IPv6) from the Internet.
- Session protection: TCP-AO (RFC 5925) where both sides support it, otherwise TCP MD5, plus GTSM TTL security (RFC 5082) on directly connected peers.
- RPKI route-origin validation: reject `invalid`, accept `valid` and `not-found`.
- AS-path filters that drop private and reserved AS numbers from Internet peers; `remove-private-as` on export where private AS numbers are used internally.
- Control-plane ACLs that allow TCP 179 only from configured peers.

### Data center notes

- eBGP per tier or per rack with private AS numbers avoids route reflectors in the underlay; see RFC 7938 and [leaf-spine design](leaf-spine.md).
- Reusing one AS number on every leaf requires `allowas-in` on the leaves or `as-override` on the spines; a unique AS per leaf needs multipath relaxation for ECMP.
- BGP unnumbered peers over IPv6 link-local addresses learned from router advertisements and removes per-link IPv4 addressing.
- Run BFD on underlay sessions so a failed link is detected in under a second.
- EVPN overlays normally peer between loopbacks and must not change the next hop on route reflectors or spines.

### Common failure patterns

| Symptom | Checks |
|---|---|
| Session never leaves `Active` or `Connect` | Route to the peer address, update source, TCP 179 filters, multihop or TTL security |
| Session resets right after `OpenSent` | Remote AS mismatch, authentication key, unsupported capability |
| `Established` with zero prefixes received | Address family not activated, import policy, peer has nothing to send, max-prefix |
| Prefix received but not installed | Next hop unreachable, better path from another protocol, RPKI invalid, AS-path loop |
| Prefix installed but not advertised | Export policy, iBGP split-horizon rule without a route reflector, `no-export` community, missing `network` statement or exact RIB match |
| Traffic takes an unexpected path | Compare all paths for the prefix and walk the best-path steps in order |
| Session flaps every few minutes | Hold-timer expiry, MTU on large updates, CPU, flapping underlying link or BFD |
| One of several equal paths is used | Multipath not enabled, AS paths differ in content, differing IGP metric |

## Troubleshooting workflow

1. Confirm the affected prefix, the neighbor, the direction of the problem, and when it started.
2. Check session state and uptime in the summary; a recent reset changes the investigation from policy to transport.
3. For a session that is not `Established`, verify reachability from the configured source address, TCP 179 filtering, AS numbers, authentication, and TTL.
4. For an established session, compare received, accepted, and advertised routes for the prefix on both sides.
5. Inspect all paths for the prefix and walk the best-path steps to explain the selection; confirm the next hop resolves.
6. Review the policy objects the neighbor references and recent changes to them before editing anything.
7. Apply the smallest policy correction and use a soft refresh, not a hard clear.
8. Verify the route sets on both peers and end-to-end forwarding; record the change and the previous policy.

## Official references

- [RFC 4271: A Border Gateway Protocol 4 (BGP-4)](https://www.rfc-editor.org/rfc/rfc4271)
- [RFC 4456: BGP Route Reflection](https://www.rfc-editor.org/rfc/rfc4456)
- [RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938)
- [RFC 8212: Default External BGP Route Propagation Behavior without Policies](https://www.rfc-editor.org/rfc/rfc8212)
- [RFC 7454: BGP Operations and Security](https://www.rfc-editor.org/rfc/rfc7454)
- [MANRS network operator guidance](https://manrs.org/netops/)
- [FRRouting BGP documentation](https://docs.frrouting.org/en/latest/bgp.html)
