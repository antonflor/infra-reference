# Junos Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for Junos routing, Border Gateway Protocol (BGP), Multiprotocol Label Switching (MPLS), interfaces, and candidate configuration management. Syntax and availability depend on platform and release.

## Safety

Inspect active state and the candidate diff before committing. Routing-session resets can interrupt traffic. Use a reviewed rollback procedure and validate candidate configuration before applying it.

## Quick reference

### BGP (Border Gateway Protocol) Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `show bgp summary` | Displays a summary of BGP peerings and their status. |
| — | `show bgp neighbor <neighbor-ip>` | Shows detailed information about a specific BGP neighbor. |
| — | `show route protocol bgp` | Displays BGP routes in the routing table. |
| — | `show route receive-protocol bgp <neighbor-ip>` | Shows routes received from a specific BGP neighbor. |
| — | `show route advertising-protocol bgp <neighbor-ip>` | Displays routes being advertised to a specific BGP neighbor. |
| — | `show bgp group <group-name>` | Displays configuration and statistics for a specific BGP group. |
| `show route summary` | `clear bgp neighbor <neighbor-ip>` | Clears a specific BGP session. **Caution:** Disruptive: resets the peer session and can withdraw routes. |
| `show route summary` | `set protocols bgp group <group-name> type <type>` | Configures a BGP group with a specific type. **Caution:** Changes candidate protocol configuration. |
| `show route summary` | `set protocols bgp group <group-name> neighbor <neighbor-ip>` | Adds a neighbor to a BGP group. **Caution:** Changes candidate protocol configuration. |
| — | `show configuration protocols bgp` | Shows the BGP configuration. |
| — | `show route advertising-protocol bgp <neighbor-ip> detail` | Shows detailed routes being advertised to a specific BGP neighbor. |
| — | `show route receive-protocol bgp <neighbor-ip> detail` | Displays detailed routes received from a specific BGP neighbor. |

### MPLS (Multiprotocol Label Switching)

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `show mpls lsp` | Shows MPLS Label Switched Path (LSP) information. |
| — | `show mpls interface` | Displays MPLS interface information. |
| — | `show route table mpls.0` | Displays the MPLS routing table. |
| — | `show mpls lsp extensive` | Shows detailed information about MPLS LSPs. |
| — | `show mpls lsp statistics` | Displays statistics for MPLS LSPs. |
| `show route summary` | `traceoptions flag mpls` | Enables MPLS-specific tracing options for debugging. **Caution:** Changes diagnostics; limit tracing and restore the previous settings. |
| — | `show route table inet.3` | Displays the MPLS forwarding table. |
| — | `show mpls lsp name <lsp-name> detail` | Shows detailed information about a specific MPLS LSP. |
| `show route summary` | `set protocols mpls label-switched-path <lsp-name> to <destination>` | Configures an MPLS LSP. **Caution:** Changes candidate protocol configuration. |
| — | `monitor traffic interface <interface-name> no-resolve` | Monitors real-time traffic on a specified interface, useful for MPLS troubleshooting. |

### Integrated Routing and Bridging (IRB)

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `show interfaces irb` | Shows Integrated Routing and Bridging (IRB) interface information. |
| — | `show interfaces irb detail` | Displays detailed information about IRB interfaces. |
| `show route summary` | `set interfaces irb unit <unit-number> family inet address <ip-address>` | Configures an IP address on an IRB interface. **Caution:** Changes candidate interface configuration. |

### General Network Management and Configuration

| Inspect first | Command | Effect / caution |
|---|---|---|
| `show route summary` | `commit` | Commits the current candidate configuration. **Caution:** Applies the candidate; inspect the candidate diff and run `commit check` first. |
| — | `commit check` | Checks the candidate configuration for errors without committing. |
| `show route summary` | `commit confirmed <time>` | Commits the configuration with an automatic rollback after a specified time unless confirmed. **Caution:** Applies the candidate with a rollback timer; inspect the candidate diff first. |
| — | `show ethernet-switching table` | Displays the Ethernet switching table (MAC address table). |
| `show route summary` | `set routing-options static route <destination> next-hop <next-hop>` | Configures a static route. **Caution:** Changes candidate routing configuration. |
| — | `show route table inet.0` | Displays the IPv4 unicast routing table. |
| — | `show route table inet6.0` | Displays the IPv6 unicast routing table. |
| — | `show route table <table-name> extensive` | Shows detailed information about a specific routing table. |
| — | `show route forwarding-table` | Displays the forwarding table. |
| — | `show route best` | Shows the best routes in the routing table. |
| — | `show route aspath-regex <as-path-regex>` | Displays routes matching a specific AS path regular expression. |
| — | `show route community <community>` | Shows routes with a specific BGP community. |
| — | `show route extensive` | Displays extensive route information. |
| — | `show route filter <filter-name>` | Shows routes matching a specific route filter. |
| — | `show route inactive` | Displays inactive routes in the routing table. |
| — | `show route next-hop <next-hop-ip>` | Shows routes with a specific next-hop. |
| — | `show route protocol <protocol>` | Displays routes learned from a specific protocol. |
| — | `show route summary` | Provides a summary of the routing table. |
| — | `show route terse` | Shows a terse output of the routing table. |

## Troubleshooting workflow

1. Confirm the device, routing instance, affected prefix or peer, and failure time.
2. Inspect interfaces, routes, and BGP or MPLS state before clearing sessions.
3. Collect relevant logs and interface or protocol counters.
4. Compare active and candidate configuration with the intended routing policy.
5. Validate the candidate and apply the smallest reviewed change with an appropriate rollback window.
6. Verify adjacency and end-to-end forwarding, then record the change and rollback configuration.

## Official references

- [Junos OS documentation](https://www.juniper.net/documentation/product/us/en/junos-os)
