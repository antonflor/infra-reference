# FortiGate Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for FortiGate administration through the FortiOS CLI, covering interfaces, routing, firewall policies, virtual private networks (VPNs), high availability, and diagnostics. Confirm commands and feature support against the deployed FortiOS release.

## Safety

Confirm the device, virtual domain (VDOM), firmware release, and active high-availability role before a change. Save a configuration backup and preserve management access. Policy deletion, tunnel resets, forced failover, configuration restore, and factory reset can interrupt service or remove configuration.

## Quick reference

### Introduction to Fortinet

Fortinet provides a range of network security products, with FortiGate being their flagship next-generation firewall (NGFW) solution. FortiGate integrates firewalling, VPN, intrusion prevention, web filtering, antivirus, and SD-WAN into a single platform.

- **Purpose**: Network security, firewall management, threat prevention, and SD-WAN.

---

### Accessing the FortiGate CLI

```text
# Via console cable (baud rate 9600)
# Via SSH
ssh admin@<fortigate-ip>

# Enter config mode for any subsystem
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config <section>

# Show current configuration
show

# Show running config (with defaults)
show full-configuration

# Get system status
get system status

# Exit config mode
end   # commit and exit
abort # discard and exit
next  # move to next entry in a list
```

---

### System and Status

```text
# Show system status (firmware, hostname, serial)
get system status

# Show hardware info
get system performance status

# Show system resource usage (CPU, memory)
diagnose sys top

# Show system uptime
get system performance status | grep Uptime

# Show FortiGate HA status
get system ha status

# Show system time
get system clock

# Set hostname
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config system global
  set hostname <hostname>
end

# Set system time
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config system ntp
  set ntpsync enable
  set syncinterval 60
  set server-mode enable
  config ntpserver
    edit 1
      set server pool.ntp.org
    next
  end
end
```

---

### Interface Configuration

```text
# View all interfaces
get system interface

# View a specific interface
get system interface <interface-name>

# Configure an interface
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config system interface
  edit <interface-name>
    set ip <ip-address> <subnet-mask>
    set allowaccess ping https ssh
    set alias "WAN Link"
    set description "Primary WAN"
    set status up
  next
end

# Configure a VLAN interface
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config system interface
  edit <vlan-name>
    set vdom root
    set ip <ip-address> <subnet-mask>
    set interface <physical-interface>
    set vlanid <vlan-id>
    set allowaccess ping
  next
end

# View interface statistics
diagnose netlink interface list
fnsysctl ifconfig <interface-name>
```

---

### Routing

```text
# Show routing table
get router info routing-table all

# Show routing table for a specific protocol
get router info routing-table ospf
get router info routing-table bgp
get router info routing-table connected
get router info routing-table static

# Show BGP summary
get router info bgp summary

# Show BGP neighbors
get router info bgp neighbors

# Show OSPF neighbors
get router info ospf neighbor

# Configure a static route
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config router static
  edit 0
    set device <interface-name>
    set gateway <gateway-ip>
    set dst <destination-network> <subnet-mask>
    set distance <administrative-distance>
    set priority <priority>
  next
end

# Configure a default route
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config router static
  edit 0
    set device <wan-interface>
    set gateway <isp-gateway>
  next
end

# Configure OSPF
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config router ospf
  set router-id <router-id>
  config area
    edit 0.0.0.0
    next
  end
  config network
    edit 1
      set prefix <network> <mask>
      set area 0.0.0.0
    next
  end
end

# Configure BGP
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config router bgp
  set as <as-number>
  set router-id <router-id>
  config neighbor
    edit <neighbor-ip>
      set remote-as <neighbor-as>
      set activate enable
    next
  end
end
```

---

### Firewall Policies

```text
# Show all firewall policies
show firewall policy

# Show policy stats (hit counts)
diagnose firewall iprope show <policy-id>

# Create a firewall policy
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config firewall policy
  edit 0
    set name "Allow-Internal-to-WAN"
    set srcintf <source-interface>
    set dstintf <destination-interface>
    set srcaddr <source-address-object>
    set dstaddr all
    set action accept
    set schedule always
    set service ALL
    set nat enable
    set logtraffic all
  next
end

# Inspect the policy before removing it
show firewall policy
# WARNING: policy deletion changes live traffic handling
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config firewall policy
  delete <policy-id>
end

# Show address objects
show firewall address
show firewall addrgrp

# Create an address object
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config firewall address
  edit "My-Server"
    set type ipmask
    set subnet <ip-address> <subnet-mask>
  next
end

# Create an address group
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config firewall addrgrp
  edit "My-Servers"
    set member "Server1" "Server2"
  next
end
```

---

### NAT Configuration

```text
# Enable NAT on a policy (outbound PAT/masquerade)
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config firewall policy
  edit <policy-id>
    set nat enable
  next
end

# Create a VIP (Virtual IP / DNAT / port forwarding)
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config firewall vip
  edit "WebServer-VIP"
    set extip <public-ip>
    set extintf <wan-interface>
    set mappedip <private-ip>
    set portforward enable
    set extport 80
    set mappedport 80
    set protocol tcp
  next
end

# View VIPs
show firewall vip

# Create an IP pool (for outbound NAT with specific source IP)
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config firewall ippool
  edit "My-IP-Pool"
    set startip <start-ip>
    set endip <end-ip>
    set type overload
  next
end
```

---

### VPN Configuration

#### IPsec VPN

```text
# Phase 1 (IKE)
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config vpn ipsec phase1-interface
  edit "VPN-to-Remote"
    set interface <wan-interface>
    set ike-version 2
    set peertype any
    set proposal aes256-sha256
    set dhgrp 14
    set remote-gw <peer-ip>
    set psksecret <pre-shared-key>
  next
end

# Phase 2 (IPsec)
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config vpn ipsec phase2-interface
  edit "VPN-to-Remote-P2"
    set phase1name "VPN-to-Remote"
    set proposal aes256-sha256
    set src-subnet <local-subnet> <mask>
    set dst-subnet <remote-subnet> <mask>
  next
end

# Check IPsec VPN status
diagnose vpn ike gateway list
diagnose vpn tunnel list

# Inspect the tunnel before resetting it
get vpn ipsec tunnel summary
# WARNING: flushing the gateway interrupts its IPsec sessions
diagnose vpn ike gateway flush name <phase1-name>
```

#### SSL VPN

> [!WARNING]
> FortiOS 7.6.3 removed SSL VPN tunnel mode from every FortiGate model, and the change carries into FortiOS 8.0. Existing tunnel-mode settings and their firewall policies are dropped on upgrade, not converted. Migrate remote access to IPsec (IKEv2, optionally over TCP 443) or ZTNA before upgrading. The former web mode continues as Agentless VPN on supported models; 2 GB RAM models lost both modes in 7.6.0. The commands below apply to FortiOS 7.4 and earlier 7.6 builds only.

```text
# Configure SSL VPN portal
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config vpn ssl web portal
  edit "full-access"
    set tunnel-mode enable
    set web-mode enable
    set ip-pools "SSLVPN_TUNNEL_ADDR1"
  next
end

# Configure SSL VPN settings
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config vpn ssl settings
  set servercert <certificate>
  set tunnel-ip-pools "SSLVPN_TUNNEL_ADDR1"
  set port 443
  set source-interface <wan-interface>
end

# Show SSL VPN sessions
get vpn ssl monitor
diagnose vpn ssl list
```

---

### High Availability (HA)

```text
# Configure HA
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config system ha
  set mode active-passive
  set group-name "HA-Cluster"
  set group-id 1
  set password <ha-password>
  set hbdev <heartbeat-interface> 50
  set session-sync-dev <sync-interface>
  set priority 200
end

# Show HA status
get system ha status
diagnose sys ha status

# WARNING: forced failover can interrupt sessions; inspect HA state above first
diagnose sys ha reset-uptime
```

---

### DHCP Server

```text
# Configure DHCP server on an interface
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config system dhcp server
  edit 0
    set interface <interface-name>
    set default-gateway <gateway-ip>
    set netmask <subnet-mask>
    set dns-server1 <dns-server-ip>
    set dns-server2 <secondary-dns-server-ip>
    config ip-range
      edit 1
        set start-ip <start-ip>
        set end-ip <end-ip>
      next
    end
    set lease-time 86400
  next
end

# View DHCP leases
diagnose sys dhcp server list
```

---

### Diagnostics and Troubleshooting

```text
# Real-time packet flow trace (debug flow)
diagnose debug flow filter addr <ip-address>
diagnose debug flow filter port <port>
diagnose debug flow trace start 100
diagnose debug enable
# ... reproduce the issue ...
diagnose debug flow trace stop
diagnose debug disable

# Packet capture (sniffer)
diagnose sniffer packet <interface> 'host <ip>' 4 100 l
# Syntax: diagnose sniffer packet <interface> '<filter>' <verbosity-1-6> <count> <timestamp>

# Ping from FortiGate
execute ping <ip-address>
execute ping-options source <source-ip>
execute ping <destination-ip>

# Traceroute
execute traceroute <ip-address>

# DNS lookup
execute nslookup name <hostname>

# Check ARP table
get system arp

# Check session table
diagnose sys session list
diagnose sys session filter dst <ip-address>
diagnose sys session filter src <ip-address>

# Check CPU and memory
diagnose hardware sysinfo cpu
diagnose hardware sysinfo memory

# View log entries
execute log filter category traffic
execute log display

# Check IPS/AV signature versions
diagnose autoupdate versions

# Test connectivity to FortiGuard
execute ping update.fortiguard.net
```

---

### SD-WAN

```text
# Show SD-WAN status
get system sdwan

# Show SD-WAN health checks
diagnose sys sdwan health-check

# Show SD-WAN interface member status
diagnose sys sdwan member

# Show SD-WAN route table
diagnose sys sdwan route

# Configure SD-WAN
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config system sdwan
  set status enable
  config members
    edit 1
      set interface <wan1-interface>
      set gateway <wan1-gateway>
    next
    edit 2
      set interface <wan2-interface>
      set gateway <wan2-gateway>
    next
  end
  config health-check
    edit "<health-check-name>"
      set server <dns-server-ip>
      set members 1 2
    next
  end
end
```

---

### Security Profiles

```text
# Show antivirus profiles
show antivirus profile

# Show web filter profiles
show webfilter profile

# Show IPS sensor configurations
show ips sensor

# Show application control profiles
show application list

# Apply security profiles to a policy
# Inspect current configuration before editing; preserve a rollback copy
show full-configuration
config firewall policy
  edit <policy-id>
    set utm-status enable
    set av-profile <av-profile-name>
    set ips-sensor <ips-sensor-name>
    set webfilter-profile <wf-profile-name>
    set application-list <app-list-name>
    set ssl-ssh-profile <ssl-profile-name>
  next
end
```

---

### Backup and Restore

```text
# Backup config via CLI (TFTP)
execute backup config tftp <filename> <tftp-server-ip>

# Backup config via FTP
execute backup config ftp <filename> <ftp-server-ip> <username> <password>

# Inspect current state and save a backup before restore
get system status
show full-configuration
# WARNING: restore replaces device configuration and can interrupt management access
execute restore config tftp <filename> <tftp-server-ip>

# Inspect current state and verify a usable backup before reset
get system status
# WARNING: factory reset removes configuration and disrupts service
execute factoryreset
```

---

### Tips for Using Fortinet

- **Regular Firmware Updates**: Keep FortiGate firmware updated — Fortinet regularly releases security patches and new features.
- **Backup Configuration**: Back up configuration before any change, especially firmware upgrades.
- **Use FortiManager**: For managing multiple FortiGate devices, FortiManager provides centralized policy management and deployment.
- **FortiAnalyzer / FortiSIEM**: Use FortiAnalyzer for centralized log management and reporting across your Fortinet devices.
- **Debug Flow**: `diagnose debug flow` is the most powerful tool for tracing why traffic is being allowed or dropped — learn to use it well.
- **Commit Before Changes**: In VDOM environments, always ensure you're working in the correct VDOM (`config vdom` → `edit <vdom-name>`).
- **Session Table**: Use `diagnose sys session` to verify traffic is being processed and natted correctly.

## Troubleshooting workflow

1. Confirm the firmware release, VDOM, HA role, affected flow, and failure time.
2. Inspect interface status, routes, policies, and existing sessions before resetting anything.
3. Collect scoped flow traces, packet captures, counters, and logs; stop diagnostics after capture.
4. Compare observed policy matches, NAT, routing, and VPN settings with the intended configuration.
5. Apply the smallest reviewed policy or configuration correction; avoid broad session resets.
6. Verify the original traffic path and HA health; record the backup and rollback state.

## Official references

- [FortiGate documentation and CLI references](https://docs.fortinet.com/product/fortigate)
