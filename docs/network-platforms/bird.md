# BIRD Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for BIRD Internet Routing Daemon inspection, protocols, routes, and configuration using `birdc`. Confirm syntax against the installed BIRD major release.

## Safety

Inspect protocols and routes before reloading configuration or disabling a protocol. Routing changes can withdraw reachability; validate the candidate configuration and preserve the previous configuration before applying a change.

## Quick reference

### BIRD Status and Protocol Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `birdc show status` | Displays the current status of the BIRD routing daemon. |
| — | `birdc show protocols` | Lists all routing protocols configured in BIRD. |
| — | `birdc show protocol <protocol-name>` | Shows detailed information about a specific routing protocol. |
| `birdc show protocols` | `birdc configure` | Reloads the configuration file. **Caution:** Reloads configuration; inspect `birdc show status` and run `birdc configure check` first. |
| — | `birdc configure check` | Checks the configuration file for errors without applying changes. |
| `birdc show protocols` | `birdc disable <protocol-name>` | Temporarily disables a routing protocol. **Caution:** Disruptive: withdraws routes from this protocol. |
| `birdc show protocols` | `birdc enable <protocol-name>` | Enables a previously disabled routing protocol. **Caution:** Activates a protocol and can change routing. |
| `birdc show protocols` | `birdc restart <protocol-name>` | Restarts a specific routing protocol. **Caution:** Disruptive: restarts a routing protocol. |
| — | `birdc log <message>` | Sends a custom log message to the BIRD log. |
| — | `birdc show events` | Displays recent routing events. |
| — | `birdc show symbols` | Lists all symbols (like route filters and functions) defined in the configuration. |
| `birdc show protocols` | `birdc debug <protocol-name> <debug-options>` | Enables debugging for a specific protocol. **Caution:** Changes diagnostic state and can increase log volume. |

### Route Display and Analysis

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `birdc show route` | Displays the routing table managed by BIRD. |
| — | `birdc show route protocol <protocol-name>` | Shows routes learned from a specific routing protocol. |
| — | `birdc show route all` | Displays all routes in the routing table, including inactive ones. |
| — | `birdc show route export <protocol-name>` | Shows routes exported by a specific protocol. |
| — | `birdc show route where <condition>` | Displays routes matching a specific condition. |
| — | `birdc show route for <ip-address>` | Shows the route for a specific IP address. |

### OSPF and BFD Sessions

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `birdc show ospf neighbors` | Lists OSPF neighbors. |
| — | `birdc show ospf state` | Displays the OSPF internal state. |
| — | `birdc show ospf interfaces` | Shows OSPF interfaces and their states. |
| — | `birdc show ospf lsadb` | Displays the OSPF link-state database. |
| — | `birdc show bfd sessions` | Lists BFD (Bidirectional Forwarding Detection) sessions. |

### Memory Usage and Interface Information

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `birdc show memory` | Shows memory usage by the BIRD daemon. |
| — | `birdc show interfaces` | Lists network interfaces known to BIRD. |
| — | `birdc show sockets` | Shows active network sockets used by BIRD. |

### Routing Tables and Filters

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `birdc show tables` | Lists routing tables managed by BIRD. |
| — | `birdc show static routes` | Displays static routes configured in BIRD. |
| — | `birdc show filters` | Displays the configured route filters. |
| — | `birdc show rip neighbors` | Lists RIP neighbors and their status. |

## Troubleshooting workflow

1. Confirm the affected prefix, peer, protocol, and BIRD release.
2. Inspect `birdc show status`, protocols, and routes without restarting sessions.
3. Collect daemon logs and neighbor-state changes with timestamps.
4. Compare protocol configuration, filters, and exported routes with the intended routing policy.
5. Validate the candidate configuration before a reviewed reload or targeted correction.
6. Verify peer state and route reachability; record the configuration and rollback file.

## Official references

- [BIRD documentation](https://bird.network.cz/?get_doc)
