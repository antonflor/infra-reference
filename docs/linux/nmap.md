# Nmap Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for Nmap target selection, discovery, port scans, service detection, scripts, and output. Use it for controlled network diagnostics with a confirmed target scope.

## Safety

Confirm the target list and scan window before sending probes. Broad scans, aggressive timing, performance tests, and some Nmap Scripting Engine (NSE) scripts can affect services. Start with target enumeration and narrowly scoped scans, then inspect the individual script documentation before expanding coverage.

## Quick reference

### Table of Contents

1. [Target Specification](#target-specification)
2. [Nmap Scan Techniques](#nmap-scan-techniques)
3. [Host Discovery](#host-discovery)
4. [Port Specification](#port-specification)
5. [Service and Version Detection](#service-and-version-detection)
6. [OS Detection](#os-detection)
7. [Timing and Performance](#timing-and-performance)
8. [NSE Scripts](#nse-scripts)
9. [Firewall / IDS Evasion and Spoofing](#firewall--ids-evasion-and-spoofing)
10. [Output](#output)
11. [Miscellaneous Nmap Flags](#miscellaneous-nmap-flags)
12. [Other Useful Nmap Commands](#other-useful-nmap-commands)

### Target Specification

- `nmap <target-ip>` — Scan a single IP
- `nmap <target-ip> <second-target-ip>` — Scan specific IPs
- `nmap <address-range>` — Scan a range
- `nmap <target-host>` — Scan a domain
- `nmap <subnet-cidr>` — Scan using CIDR notation
- `nmap -iL targets.txt` — Scan targets from a file
- `nmap --exclude <target-ip>` — Exclude listed hosts
- `nmap --excludefile exclude.txt` — Exclude hosts listed in a file

### Nmap Scan Techniques

- `nmap <target-ip> -sS` — TCP SYN port scan (default, requires root)
- `nmap <target-ip> -sT` — TCP connect port scan (default without root privilege)
- `nmap <target-ip> -sU` — UDP port scan
- `nmap <target-ip> -sA` — TCP ACK port scan (firewall rule detection)
- `nmap <target-ip> -sW` — TCP Window port scan
- `nmap <target-ip> -sM` — TCP Maimon port scan
- `nmap <target-ip> -sN` — TCP Null scan (no flags set)
- `nmap <target-ip> -sF` — TCP FIN scan
- `nmap <target-ip> -sX` — TCP Xmas scan (FIN, PSH, URG flags)

### Host Discovery

- `nmap <address-range> -sL` — No scan; list targets only
- `nmap <subnet-cidr> -sn` — Disable port scanning; host discovery only (ping scan)
- `nmap <address-range> -Pn` — Disable host discovery; port scan only (treat all hosts as online)
- `nmap <target-ip> -PS22,80,443` — TCP SYN discovery on specific ports
- `nmap <target-ip> -PA80` — TCP ACK discovery
- `nmap <target-ip> -PU53` — UDP discovery
- `nmap <target-ip> -PE` — ICMP echo request discovery
- `nmap <target-ip> -PR` — ARP discovery (local network only)
- `nmap <target-ip> -n` — Never do DNS resolution
- `nmap <target-ip> -R` — Always resolve DNS

### Port Specification

- `nmap <target-ip> -p 21` — Port scan for a single port
- `nmap <target-ip> -p 21-100` — Port range
- `nmap <target-ip> -p U:53,T:21-25,80` — Scan multiple TCP and UDP ports
- `nmap <target-ip> -p-` — Scan all 65535 ports
- `nmap <target-ip> -p http,https` — Port scan from service name
- `nmap <target-ip> -F` — Fast scan (top 100 most common ports)
- `nmap <target-ip> --top-ports 1000` — Scan the top 1000 most common ports

### Service and Version Detection

- `nmap <target-ip> -sV` — Attempts to determine the version of the service running on port
- `nmap <target-ip> -sV --version-intensity 8` — Intensity level 0–9; higher = more accurate but slower
- `nmap <target-ip> -sV --version-light` — Light mode; lower accuracy, faster
- `nmap <target-ip> -sV --version-all` — Intensity level 9; highest accuracy, slowest
- `nmap <target-ip> -A` — Enables OS detection, version detection, script scanning, and traceroute

### OS Detection

- `nmap <target-ip> -O` — Remote OS detection using TCP/IP stack fingerprinting
- `nmap <target-ip> -O --osscan-limit` — Only attempt OS detection if at least one open and one closed TCP port are found
- `nmap <target-ip> -O --osscan-guess` — Makes Nmap guess more aggressively
- `nmap <target-ip> -O --max-os-tries 1` — Set the maximum number of OS detection tries against a target

### Timing and Performance

- `nmap <target-ip> -T0` — Paranoid; slowest, best for IDS evasion
- `nmap <target-ip> -T1` — Sneaky; slow IDS evasion
- `nmap <target-ip> -T2` — Polite; slows down to use less bandwidth and fewer target resources
- `nmap <target-ip> -T3` — Normal; default speed
- `nmap <target-ip> -T4` — Aggressive; faster, assumes reliable network
- `nmap <target-ip> -T5` — Insane; fastest, may miss results on slow networks
- `nmap <target-ip> --min-rate 1000` — Send packets no slower than 1000 per second
- `nmap <target-ip> --max-retries 1` — Reduce retransmissions for faster scans

### NSE Scripts

- `nmap <target-ip> -sC` — Scan with default NSE scripts
- `nmap <target-ip> --script default` — Same as above
- `nmap <target-ip> --script=banner` — Scan with a single script (banner)
- `nmap <target-ip> --script=http*` — Scan with wildcard (all http scripts)
- `nmap <target-ip> --script=http,banner` — Run multiple scripts
- `nmap <target-ip> --script "not intrusive"` — Run default scripts, exclude intrusive ones
- `nmap <target-ip> --script vuln` — Run vulnerability detection scripts
- `nmap <target-ip> --script smb-vuln*` — Check for SMB vulnerabilities
- `nmap <target-ip> --script-args <key=value>` — Pass arguments to scripts
- `nmap --script-updatedb` — Update the NSE script database

### Firewall / IDS Evasion and Spoofing

- `nmap <target-ip> -f` — Fragment packets into tiny IP packets; harder for packet filters
- `nmap <target-ip> -mtu 32` — Set a custom MTU offset size (must be multiple of 8)
- `nmap -D <decoy-ip-1>,<decoy-ip-2>,ME <target-ip>` — Decoy scan; use fake source IPs to obscure origin
- `nmap <target-ip> -S <source-ip>` — Spoof source IP address (requires --send-eth or root)
- `nmap <target-ip> -e <interface>` — Use a specific network interface
- `nmap <target-ip> -g 53` — Use a specific source port (e.g., DNS port 53 to evade firewalls)
- `nmap <target-ip> --source-port 53` — Same as above
- `nmap <target-ip> --data-length 25` — Append random data to packets to evade detection
- `nmap <target-ip> --randomize-hosts` — Randomize target host scan order
- `nmap <target-ip> --badsum` — Send packets with incorrect checksums (for testing IDS/IPS response)
- `nmap <target-ip> --proxies socks4://<proxy-host>:<port>` — Route traffic through SOCKS4 or HTTP proxy

### Output

- `nmap <target-ip> -oN output.txt` — Normal output to a file
- `nmap <target-ip> -oX output.xml` — XML output to a file
- `nmap <target-ip> -oG output.gnmap` — Grepable output to a file
- `nmap <target-ip> -oA output` — Output in all formats (normal, XML, grepable)
- `nmap <target-ip> -v` — Increase verbosity
- `nmap <target-ip> -vv` — Increase verbosity further
- `nmap <target-ip> --reason` — Display the reason a port is in a particular state
- `nmap <target-ip> --open` — Only show open ports
- `nmap <target-ip> --packet-trace` — Show all packets sent and received
- `nmap <target-ip> --iflist` — Print host interfaces and routes (for debugging)
- `nmap <target-ip> --resume output.gnmap` — Resume an aborted scan from a grepable file

### Miscellaneous Nmap Flags

- `nmap -6 <ipv6-address>` — Enable IPv6 scanning
- `nmap -h` — Display help summary
- `nmap --version` — Display Nmap version number
- `nmap --privileged` — Assume that the user is fully privileged
- `nmap --unprivileged` — Assume the user lacks raw socket privileges

### Other Useful Nmap Commands

**Full port and service scan**
```bash
nmap -sS -sV -sC -O -A -p- <target-ip>
```

**Fast Network Sweep**
```bash
nmap -sn <subnet-cidr>
```

**Scan for Open Web Ports**
```bash
nmap -p 80,443,8080,8443 <subnet-cidr>
```

**Detect Heartbleed Vulnerability**
```bash
nmap -sV --script ssl-heartbleed <target-ip>
```

**Check for SMB Vulnerabilities (EternalBlue)**
```bash
nmap --script smb-vuln-ms17-010 -p 445 <target-ip>
```

**Banner Grabbing**
```bash
nmap -sV --script=banner <target-ip>
```

**HTTP Enumeration**
```bash
nmap --script http-enum -p 80,443 <target-ip>
```

**DNS Brute Force**
```bash
nmap --script dns-brute example.com
```

**Export Results and View in Browser**
```bash
nmap -oX scan.xml <subnet-cidr> && xsltproc scan.xml -o scan.html
```

## Troubleshooting workflow

1. Confirm the target scope, scan type, privileges, and expected service.
2. Inspect local interface and route state, then enumerate the intended targets before sending probes.
3. Collect the exact command, scan timestamps, output, and relevant target-side logs.
4. Compare results with firewall rules, routing, service listeners, and the chosen scan assumptions.
5. Adjust one scan setting at a time and repeat a narrowly scoped check.
6. Verify the result with service-side evidence and record any configuration change and rollback state.

## Official references

- [Nmap reference guide](https://nmap.org/book/man.html)
- [NSE script documentation](https://nmap.org/nsedoc/)
