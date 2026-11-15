# BIRD Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for BIRD Internet Routing Daemon inspection, protocols, routes, and configuration using `birdc`. Confirm syntax against the installed BIRD major release.

## Safety

Inspect protocols and routes before reloading configuration or disabling a protocol. Routing changes can withdraw reachability; validate the candidate configuration and preserve the previous configuration before applying a change.

## Quick reference

### Release notes

Commands are for BIRD 2.x and 3.x, where one daemon and one `birdc` handle IPv4 and IPv6. BIRD 1.x used a separate `bird6`/`birdc6` pair. BIRD 3 is multithreaded and keeps the 2.x CLI with small output differences. `birdc -r` opens a restricted, read-only session, which is the safer default for inspection.

### Status and protocols

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `birdc show status` | Daemon version, router ID, uptime, and last reconfiguration. |
| — | `birdc show protocols` | One line per protocol instance with state and since-time. |
| — | `birdc show protocols all <protocol-name>` | Detailed state, channels, and route counters for one instance. |
| — | `birdc show interfaces summary` | Interfaces and addresses known to BIRD. |
| — | `birdc show memory` | Memory usage by category. |
| — | `birdc show symbols` | Lists configured names; add `table`, `filter`, or `protocol` to narrow. |

### Configuration changes

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `bird -p -c /etc/bird/bird.conf` | Parses a configuration file and exits without touching the running daemon. |
| — | `birdc configure check` | Asks the running daemon to parse its configuration without applying it. |
| `birdc configure check` | `birdc configure timeout 120` | Applies the configuration and reverts unless confirmed within 120 seconds. **Caution:** Changes routing; follow with `birdc configure confirm`. |
| `birdc configure check` | `birdc configure` | Applies the configuration with no automatic revert. **Caution:** Changed protocols can restart. |
| `birdc show status` | `birdc configure undo` | Returns to the previous configuration. **Caution:** Changes routing again. |
| `birdc show protocols` | `birdc reload in <protocol-name>` | Re-evaluates import filters using route refresh, without a session reset. |
| `birdc show protocols` | `birdc reload out <protocol-name>` | Re-evaluates export filters and re-advertises. |
| `birdc show protocols` | `birdc disable <protocol-name>` | Shuts a protocol instance down. **Caution:** Disruptive: withdraws its routes. |
| `birdc show protocols` | `birdc enable <protocol-name>` | Starts a disabled instance. **Caution:** Can change routing. |
| `birdc show protocols` | `birdc restart <protocol-name>` | Restarts an instance. **Caution:** Disruptive: resets the session. |
| `birdc show protocols` | `birdc debug <protocol-name> <all\|off\|states,routes,filters,events,packets>` | Changes protocol debug logging. **Caution:** Can produce large logs; turn it off afterwards. |

### Routes

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `birdc show route` | Routes in the default tables. |
| — | `birdc show route table <table-name>` | Routes in one table, such as `master4` or `master6`. |
| — | `birdc show route for <ip-address>` | Longest-prefix match for an address. |
| — | `birdc show route <prefix> all` | Every attribute of the routes for a prefix. |
| — | `birdc show route protocol <protocol-name>` | Routes learned from one protocol instance. |
| — | `birdc show route export <protocol-name>` | Routes that pass the export filter toward a protocol. |
| — | `birdc show route noexport <protocol-name>` | Routes the export filter rejects. |
| — | `birdc show route where <filter-expression>` | Routes matching an expression, such as `bgp_path.last = 64512`. |
| — | `birdc show route count` | Route totals per table. |

### Protocol-specific state

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `birdc show ospf neighbors` | OSPF adjacencies and states. |
| — | `birdc show ospf interface` | OSPF interfaces, areas, cost, and DR state. |
| — | `birdc show ospf state` | Topology as seen by the link-state database. |
| — | `birdc show ospf lsadb` | Link-state database contents. |
| — | `birdc show bfd sessions` | BFD sessions, state, and intervals. |
| — | `birdc show static` | Static routes and whether their next hops are usable. |
| — | `birdc show rip neighbors` | RIP neighbors. |

## Troubleshooting workflow

1. Confirm the affected prefix, peer, protocol, and BIRD release.
2. Inspect `birdc show status`, protocols, and routes without restarting sessions.
3. Collect daemon logs and neighbor-state changes with timestamps.
4. Compare protocol configuration, filters, and exported routes with the intended routing policy.
5. Validate the candidate configuration before a reviewed reload or targeted correction.
6. Verify peer state and route reachability; record the configuration and rollback file.

## Official references

- [BIRD documentation](https://bird.network.cz/?get_doc)
- [BIRD 2 remote control reference](https://bird.network.cz/?get_doc&v=20&f=bird-4.html)
